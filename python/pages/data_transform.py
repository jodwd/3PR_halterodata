import sqlite3 as sql
import pandas as pd
import math
import os
import csv

#Recalcul de l'IWF par année (permet de recalculer correctement les minimes)
def sinclair_history(total, pdc, sexe, annee):
    print(total)

    if annee<2023:
        if sexe == 'M':
            a = 0.751945030
            b = 175.508
        else:
            a = 0.783497476
            b = 153.655
    if annee>=2023:
        if sexe == 'M':
            a = 0.722762521
            b = 193.609
        else:
            a = 0.787004341
            b = 153.757
    res = total*(10**(a*((math.log10(pdc/b))**2)))
    return res;

#Recalcul du total par mouvement
def resultat(mvmt1, mvmt2, mvmt3):
    if mvmt3> 0:
        res = mvmt3
    elif mvmt2> 0:
        res = mvmt2
    elif mvmt1> 0:
        res = mvmt1
    else:
        res = 0
    return res;

#Recalcul du total par mouvement pour les U10/U13
def resultatU13(mvmt1, mvmt2, mvmt3):
    if mvmt2>0 and mvmt3>0:
        res = mvmt2+mvmt3
    elif mvmt1>0 and mvmt3> 0:
        res = mvmt1+mvmt3
    elif mvmt1> 0 and mvmt2>0:
        res = mvmt1+mvmt2
    else:
        res = 0
    return res;
def cate_master(annee_naissance, annee_saison, sexe, cate_poids):
    if annee_saison-annee_naissance<35:
        res = ''
    else:
        cat_age = 35 + 5*math.floor((annee_saison-annee_naissance)/5)
        if sexe == 'F':
            s = 'W'
        else:
            s = 'M'
        res = s + cat_age + ' ' + sexe + ' ' + cate_poids
    return res;
def cate_poids(cate):
    cate_poids_index = (cate.rfind(' ')-len(cate)+3)
    res = cate[cate_poids_index:]
    return res;
def cate_age(cate):
    if cate[0] == 'M' or cate[0] == 'W':
        res = 'SEN'
    else:
        cate_age_end_index = cate.find(' ')
        res = cate[0 : cate_age_end_index]
    return res;



def main_code():
    try:
        #Connection à la base SQLite
        conn = sql.connect(database="dataltero.db")
        cur = conn.cursor()

        cur.execute("DROP TABLE IF EXISTS haltero_data_full")

        #On remplace les "faux" espaces du data par des "vrais" espaces
        dirname = os.path.dirname(__file__)
        path_csv = os.path.join(dirname, '../haltero_data_full.csv')
        #path_csv = 'C:/Users/joris/PycharmProjects/halterodata/python/haltero_data_full.csv'
        print(path_csv)
        with open(path_csv, 'r', newline='', encoding='utf-8') as file:
            content = file.read()
            modified_content = content
            #content = content.replace('\u00A0', ' ')  # Replace non-breaking spaces with regular spaces
            modified_content = content.replace('1,2,3,ARR,1,2,3', 'Arr1,Arr2,Arr3,Arr,EpJ1,EpJ2,EpJ3')  # Replace non-breaking spaces with regular spaces

        with open(path_csv, 'w', newline='', encoding='utf-8') as file:
            file.write(modified_content)

        df = pd.read_csv(path_csv, sep=',')
        df.columns = df.columns.str.strip()

        df.to_sql("df", conn, if_exists="replace")

        ##create the table

        conn.execute(
            """
            create table haltero_data_full as 
            select * from df
            """)


        #Suppression des tables pour cleaning
        cur.execute("DROP TABLE IF EXISTS CLUB")
        cur.execute("DROP TABLE IF EXISTS COMPET")
        cur.execute("DROP TABLE IF EXISTS ATHLETE")
        cur.execute("DROP TABLE IF EXISTS COMPET_ATHLETE")
        cur.execute("DROP TABLE IF EXISTS ATHLETE_PR")

        #Création des fonctions
        conn.create_function("mvmt_resultat", 3 , resultat)
        conn.create_function("mvmt_resultatU13", 3 , resultatU13)
        conn.create_function("coeff_sinclair", 4 , sinclair_history)
        conn.create_function("categorie_master", 4 , cate_master)
        conn.create_function("categorie_poids", 1 , cate_poids)
        conn.create_function("categorie_age", 1 , cate_age)

        #TABLE CLUB
        for res in cur.execute(
            """ CREATE table CLUB as 
                SELECT Club, Ligue from (
                  select
                     Club
                ,    substr(Competition, 1, instr(Competition, ' ')-1) as Ligue
                ,    count(1)
                ,    row_number() over(partition by Club order by count(1) desc) as row_num
                 
                FROM haltero_data_full
                    group by Club,  substr(Competition, 1, instr(Competition, ' ')-1)
                    ORDER BY Club, count(1) desc) as data_club
                where data_club.row_num=1
                    """):
            print(res)

        for res in cur.execute(
            """ CREATE table COMPET as
                SELECT distinct
                hfd.Competition                  as "NomCompetition"
            ,   substr(substr(hfd.Competition, instr(hfd.Competition, '-')+2, length(hfd.Competition)-instr(hfd.Competition, '-')), 1,
                    length(substr(hfd.Competition, instr(hfd.Competition, '-')+2, length(hfd.Competition)-instr(hfd.Competition, '-')))-15) as "NomCompetitionCourt"
            ,   substr(hfd.Competition, 1, 3)    as "LigueCompetition"
            ,   dat."DateCompet"
            ,   dat."AnneeCompet" 
            ,   dat."MoisCompet"
            ,   dat."AnneeMois"
            ,  '' as  "SemaineCompet"
            ,   strftime('%Y', date(dat."DateCompet", '-8 months')) || '-' || strftime('%Y', date(dat."DateCompet", '+4 months')) as "Saison"
            ,   cast(strftime('%Y', date(dat."DateCompet", '+4 months')) as Integer) as "SaisonAnnee"
                   
                   FROM haltero_data_full as hfd
                   LEFT JOIN (SELECT
                        Competition
                   ,    substr(Competition, length(Competition)-3,4) || '-' ||
                        case substr(Competition,
                            length(Competition)-7,3)
                                when 'Jan' then '01'
                                when 'Fév' then '02'
                                when 'Mar' then '03'
                                when 'Avr' then '04'
                                when 'Mai' then '05'
                                when 'Jui' then '06'
                                when 'Jul' then '07'
                                when 'Aoû' then '08'
                                when 'Sep' then '09'
                                when 'Oct' then '10'
                                when 'Nov' then '11'
                                when 'Déc' then '12'
                              end  || '-' ||
                            substr(Competition, length(Competition)-10,2) as "DateCompet"
                    ,   substr(Competition, length(Competition)-3,4) as "AnneeCompet" 
                    ,   case substr(Competition,
                        length(Competition)-7,3)
                            when 'Jan' then '01'
                            when 'Fév' then '02'
                            when 'Mar' then '03'
                            when 'Avr' then '04'
                            when 'Mai' then '05'
                            when 'Jui' then '06'
                            when 'Jul' then '07'
                            when 'Aoû' then '08'
                            when 'Sep' then '09'
                            when 'Oct' then '10'
                            when 'Nov' then '11'
                            when 'Déc' then '12'
                          end as "MoisCompet"
                    ,   substr(Competition, length(Competition)-3,4) 
                        || '_' ||
                        case substr(Competition,
                            length(Competition)-7,3)
                                when 'Jan' then '01'
                                when 'Fév' then '02'
                                when 'Mar' then '03'
                                when 'Avr' then '04'
                                when 'Mai' then '05'
                                when 'Jui' then '06'
                                when 'Jul' then '07'
                                when 'Aoû' then '08'
                                when 'Sep' then '09'
                                when 'Oct' then '10'
                                when 'Nov' then '11'
                                when 'Déc' then '12'
                              end as "AnneeMois"
                    ,  '' as  "SemaineCompet"
                        FROM haltero_data_full) as dat
                        on dat.Competition = hfd.Competition
                   """):
            print(res)


        #Table athlète
        # Conversion du numéro de licence pour les athlètes en doublon (càd nom + date naissance identique = plusieurs licences)
        # Licence max remplacée par licence min
        for res in cur.execute(
            """ CREATE table ATHLETE as
                select
                    dat.Nom                             as "Nom"
                ,   dat."Date Naissance"                as "DateNaissance"
                ,   dat.Nom || dat."Date Naissance"     as "AthleteID"
                ,   dat.Licence                         as "Licence"
                ,   nat.NAT                             as "Nationalite"               
                
                from (SELECT distinct Nom, "Date Naissance", max(Licence) as Licence from haltero_data_full group by Nom, "Date Naissance") as dat
                left join (Select distinct Licence, NAT, "Date Competition",
                                ROW_NUMBER() OVER (
                                    PARTITION BY Licence, "Date Competition"
                                    ORDER BY "Date Competition" DESC
                                ) as row_num
                         from haltero_data_full
                         order by Licence, "Date Competition" desc) as nat
                         on nat.licence = dat.licence
                         and nat.row_num=1
                group by dat.nom, dat."Date Naissance"
                   """):
            print(res)

        for res in cur.execute("""SELECT   distinct      "NomCompetition"
            ,  "NomCompetitionCourt"
            FROM COMPET"""):
            print(res)

        # Table Compétition Athlète
        # Un athlète peut théoriquement changer de club durant la saison donc le club de l'athlète est rattaché à la compétition
        #CREATE table COMPET_ATHLETE as
        for res in cur.execute(
            """ CREATE table COMPET_ATHLETE as
                select
                    dat.Licence                                        as "CATLicence"
                ,   dat.Competition                                    as "CATNomCompetition"
                ,   dat.Club                                           as "CATClub"
                ,   dat.Nom || dat."Date Naissance"                    as "AthleteID"
                ,   dat."P.C."                                         as "PoidsDeCorps"
                ,   dat.Arr1
                ,   dat.Arr2
                ,   dat.Arr3
                ,   mvmt_resultat(dat.Arr1, dat.Arr2, dat.Arr3)         as "Arrache"
                ,   mvmt_resultatU13(dat.Arr1, dat.Arr2, dat.Arr3)      as "ArracheU13"
                ,   dat.EpJ1                                            as "EpJ1"
                ,   dat.EpJ2                                            as "EpJ2"
                ,   dat.EpJ3                                            as "EpJ3"   
                ,   mvmt_resultat(dat.EpJ1, dat.EpJ2, dat.EpJ3)         as "EpJete"
                ,   mvmt_resultatU13(dat.EpJ1, dat.EpJ2, dat.EpJ3)      as "EpJeteU13"
                ,   mvmt_resultat(dat.Arr1, dat.Arr2, dat.Arr3) +
                    mvmt_resultat(dat.EpJ1, dat.EpJ2, dat.EpJ3)         as "PoidsTotal"
                ,   mvmt_resultatU13(dat.Arr1, dat.Arr2, dat.Arr3) +
                    mvmt_resultatU13(dat.EpJ1, dat.EpJ2, dat.EpJ3)      as "TotalU13"
                ,   coeff_sinclair(
                            mvmt_resultat(dat.Arr1, dat.Arr2, dat.Arr3) + mvmt_resultat(dat.EpJ1, dat.EpJ2, dat.EpJ3)
                        ,   cast(replace(dat."P.C.", ',' , '.') as decimal)
                        ,   case when
                            dat.Catégorie like '%F%'
                                   then 'F'
                                   else 'M'
                               end
                       ,   cast(comp."SaisonAnnee" as Integer))                          as "IWF_Calcul"
                ,   dat.Série                                                            as "Serie"
                ,   categorie_poids(dat.Catégorie)                                       as "CatePoids"
                ,   categorie_age(dat.Catégorie)                                         as "CateAge"
                ,   replace(dat.Catégorie, cast('\xa0' as text), ' ')                    as "Categorie"               
                ,   dat.IWF
                ,   case when dat.Catégorie like '%F%' then 'F' else 'M' end             as "Sexe"
   
                    from haltero_data_full as dat
                    left join COMPET as comp
                        on comp.NomCompetition = dat.competition
                   """):
            print(res)

        for res in cur.execute(
                """ CREATE table ATHLETE_PR as
                    select
                        dat.Nom || dat."Date Naissance"  as "AthleteID"
                    ,   comp.SaisonAnnee
                    ,   pra."MaxIWF" as "MaxIWF"
                    ,   max(cat."IWF_Calcul") as "MaxIWFSaison"
                    
                        from haltero_data_full as dat
                        left join COMPET as comp
                            on comp.NomCompetition = dat.competition
                        left join COMPET_ATHLETE as cat
                            on cat."AthleteID" = (dat.Nom || dat."Date Naissance")
                            and cat.CATNomCompetition = comp.NomCompetition
                        left join (select
                            dat.Nom || dat."Date Naissance"  as "AthleteID"
                        ,   max(cat."IWF_Calcul") as "MaxIWF"
                        
                            from haltero_data_full as dat
                            left join COMPET_ATHLETE as cat
                                on cat."AthleteID" = (dat.Nom || dat."Date Naissance")
                            group by dat.Nom || dat."Date Naissance") as pra
                            on pra."AthleteID" = dat.Nom || dat."Date Naissance" 
                            
                        group by dat.Nom || dat."Date Naissance" 
                             ,   comp.SaisonAnnee
                             ,   pra."MaxIWF"
                       """):
            print(res)

        for res in cur.execute(
            """SELECT * FROM
                        (SELECT distinct
                            ath.Nom             as "Nom"
                        ,   clb.Club            as "Club"
                        ,   clb.Ligue           as "Ligue"
                        ,   cat."Sexe"          as "Sexe"
                        ,   cat.Arrache         as "Arr"
                        ,   cat.EpJete          as "EpJ"
                        ,   cat.PoidsTotal      as "Total"
                        ,   cat.PoidsDeCorps    as "PdC"    
                        ,   apr.SaisonAnnee     as "SaisonAnnee"
                        ,   apr.MaxIWFSaison    as "Max IWF Saison"
                        ,   apr.MaxIWF          as "Max IWF"
                        ,   row_number() over(partition by ath.Nom, apr."SaisonAnnee" order by apr.MaxIWFSaison desc) as "RowNum"
                      FROM ATHLETE as ath 
                      LEFT JOIN COMPET_ATHLETE as cat on cat.AthleteID= ath.AthleteID 
                      LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition 
                      LEFT JOIN CLUB as clb on clb.Club = cat.CATClub
                      LEFT JOIN ATHLETE_PR as apr on apr.AthleteID = ath.AthleteID and apr.SaisonAnnee = cmp.SaisonAnnee)
                  WHERE Nom='Benjamin\xa0FERRE'"""):
            print(res)

    finally:
        # closing database connection.
        if conn:
            cur.close()
            conn.close()

main_code()