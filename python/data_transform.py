import sqlite3 as sql
import pandas as pd
import math


def sinclair_history(total, pdc, sexe, annee):
    print(total)
    if sexe == 'M':
        res = total*(10**(0.751945030*((math.log10(pdc/175.508))**2)))
    else:
        res = total*(10**(0.783497476*((math.log10(pdc/153.655))**2)))
    return res


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
def main_code():
    try:
        conn = sql.connect(database="dataltero.db")
        cur = conn.cursor()

        df = pd.read_csv('C:/Users/joris/PycharmProjects/halterodata/output/haltero_data_full_2.csv', sep=';')
        df.columns = df.columns.str.strip()
        print(2)
        #df.to_sql("haltero_full_data", conn)

        #Suppression des tables pour cleaning
        cur.execute("DROP TABLE IF EXISTS CLUB")
        cur.execute("DROP TABLE IF EXISTS COMPET_DATES")
        cur.execute("DROP TABLE IF EXISTS ATHLETES")

        #Création des fonctions
        conn.create_function("mvmt_resultat", 3 , resultat)
        conn.create_function("mvmt_resultatU13", 3 , resultatU13)
        conn.create_function("coeff_sinclair", 4 , sinclair_history)
        #TABLE CLUB
        for res in cur.execute(
            """ CREATE table CLUB as 
                SELECT Club, Ligue from (
                  select
                     Club
                ,    substr(Competition, 1, instr(Competition, ' ')-1) as Ligue
                ,    count(1)
                ,    row_number() over(partition by Club order by count(1) desc) as row_num
                 
                FROM haltero_full_data
                    group by Club,  substr(Competition, 1, instr(Competition, ' ')-1)
                    ORDER BY Club, count(1) desc) as data_club
                where data_club.row_num=1
                    """):
            print(res)

        for res in cur.execute(
            """ CREATE table COMPET_DATES as
                SELECT
                hfd.Competition                 as "NomCompetition"
            ,   substr(hfd.Competition, 1, 3)    as "LigueCompetition"
            ,   dat."Date Compet"
            ,   dat."Annee Compet" 
            ,   dat."Mois Compet"
            ,  '' as  "Semaine Compet"
            ,   strftime('%Y', date(dat."Date Compet", '-4 months')) || '-' || strftime('%Y', date(dat."Date Compet", '+8 months')) as "Saison"
            ,   strftime('%Y', date(dat."Date Compet", '+8 months')) as "Saison Annee"
                   
                   FROM haltero_full_data as hfd
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
                                when 'Jun' then '06'
                                when 'Jul' then '07'
                                when 'Aou' then '08'
                                when 'Sep' then '09'
                                when 'Oct' then '10'
                                when 'Nov' then '11'
                                when 'Déc' then '12'
                              end  || '-' ||
                            substr(Competition, length(Competition)-10,2) as "Date Compet"
                    ,   substr(Competition, length(Competition)-3,4) as "Annee Compet" 
                    ,   case substr(Competition,
                        length(Competition)-7,3)
                            when 'Jan' then '01'
                            when 'Fév' then '02'
                            when 'Mar' then '03'
                            when 'Avr' then '04'
                            when 'Mai' then '05'
                            when 'Jun' then '06'
                            when 'Jul' then '07'
                            when 'Aou' then '08'
                            when 'Sep' then '09'
                            when 'Oct' then '10'
                            when 'Nov' then '11'
                            when 'Déc' then '12'
                          end as "Mois Compet"
                    ,  '' as  "Semaine Compet"
                        FROM haltero_full_data) as dat
                        on dat.Competition = hfd.Competition
                   """):
            print(res)


        #Table athlète
        # Conversion du numéro de licence pour les athlètes en doublon (càd nom + date naissance identique = plusieurs licences)
        # Licence max remplacée par licence min
        for res in cur.execute(
            """ CREATE table ATHLETES as
                select
                    dat.Nom
                ,   dat."Date Naissance"
                ,   dat.Licence as "Licence"
                ,   nat.NAT  as "Nationalite" 
                
                from (SELECT distinct Nom, "Date Naissance", max(Licence) as Licence from haltero_full_data group by Nom, "Date Naissance") as dat
                left join (Select distinct Licence, NAT, "Date Competition",
                                ROW_NUMBER() OVER (
                                    PARTITION BY Licence, "Date Competition"
                                    ORDER BY "Date Competition" DESC
                                ) as row_num
                         from haltero_full_data
                         order by Licence, "Date Competition" desc) as nat
                         on nat.licence = dat.licence
                         and nat.row_num=1
                group by dat.nom, dat."Date Naissance"
                   """):
            print(res)

        # Table Compétition Athlète
        # Un athlète peut théoriquement changer de club durant la saison donc le club de l'athlète est rattaché à la compétition
        for res in cur.execute(
            """
                select
                    dat.Licence,
                    dat.Competition,
                    dat.Club,
                    dat."Poids de Corps",
                    dat.Arr1,
                    dat.Arr2,
                    dat.Arr3,
                    mvmt_resultat(dat.Arr1, dat.Arr2, dat.Arr3) as "Arrache",
                    mvmt_resultatU13(dat.Arr1, dat.Arr2, dat.Arr3) as "ArracheU13",
                    dat.EpJ1,
                    dat.EpJ2,
                    dat.EpJ3,   
                    mvmt_resultat(dat.EpJ1, dat.EpJ2, dat.EpJ3) as "EpJeté",
                    mvmt_resultatU13(dat.EpJ1, dat.EpJ2, dat.EpJ3) as "EpJeteU13",
                    mvmt_resultat(dat.Arr1, dat.Arr2, dat.Arr3) +
                    mvmt_resultat(dat.EpJ1, dat.EpJ2, dat.EpJ3) as "PoidsTotal",
                    mvmt_resultatU13(dat.Arr1, dat.Arr2, dat.Arr3) +
                    mvmt_resultatU13(dat.EpJ1, dat.EpJ2, dat.EpJ3)  as "TotalU13",
                    coeff_sinclair(
                            mvmt_resultat(dat.Arr1, dat.Arr2, dat.Arr3) + mvmt_resultat(dat.EpJ1, dat.EpJ2, dat.EpJ3)
                        ,   cast(replace(dat."Poids de Corps", ',' , '.') as decimal)
                        ,   case when
                            dat.Catégorie like '%F%'
                                   then 'F'
                                   else 'M'
                               end
                       ,   2022) as "IWF_Calcul",
                    dat.Série,
                    dat.Catégorie,
                    dat.IWF,
                    case when dat.Catégorie like '%F' then 'F' else 'M' end  as "Sexe"
   
                    from haltero_full_data as dat
                   """):
            print(res)

    #sinclair_history(
    #                iif(dat.Arr3>0, dat.Arr3,
    #                    iif(dat.Arr2>0, dat.Arr2,
    #                        iif(dat.Arr1>0, Arr1, 0))) +
    #                iif(dat.EpJ3>0 and dat.EpJ2>0 , dat.EpJ2+dat.EpJ3,
    #                    iif(dat.EpJ3>0 and dat.EpJ1>0, dat.EpJ1+dat.EpJ3,
    #                        iif(dat.EpJ1+dat.EpJ2>0, dat.EpJ1+dat.EpJ2, 0))) , dat."Poids de Corps", case when dat.Catégorie like '%F' then 'F' else 'M' end , cast(right(dat.Competition, 4) as integer)) as "IWF_Calcul",
    #                    coeff_sinclair(
   #                         mvmt_resultat(dat.Arr1, dat.Arr2, dat.Arr3) + mvmt_resultat(dat.EpJ1, dat.EpJ2, dat.EpJ3)
  #                     ,   dat."Poids de Corps"
  #                     ,   case when
  #                             dat.Catégorie like '%F%'
  #                                 then 'F'
  #                                 else 'M'
  #                             end
  #                     ,   2022) as "IWF_Calcul",
  # # ,  left(SaisonAnnee;Annee Mois;Âge Sportif;Age;CatégorieAge;Sexe;Catégorie Poids;Max Saison;LigueCompet;Ligue;IWF_Points;ID Compet;Doublons;Colonne2


    finally:
        # closing database connection.
        if conn:
            cur.close()
            conn.close()

main_code()
