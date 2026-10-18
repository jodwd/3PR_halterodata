
  class String

    def indexes sub_string,start=0
      index = self[start..-1].index(sub_string)
      return [] unless index
      [index+start] + indexes(sub_string,index+start+1)
    end

  end
  
require 'mechanize'
require 'csv'
require 'byebug'
mechanize = Mechanize.new
stuff=" "
stuff_xml=" "
xml=" "
s=0
t=0
text_csv=Array.new

#On supprime le csv de sortie des données
output_path = "C:/Users/Joris/PycharmProjects/halterodata/haltero_data_full.csv"
output_path_new = "C:/Users/Joris/PycharmProjects/halterodata/haltero_data_full_" + Time.now.strftime("%d_%m_%Y_%H_%M") +  ".csv"
File.rename(output_path, output_path_new) if File.exist?(output_path)

#26/02/2023 : <6900 athlètes, à checker en 2024
#05/11/2023 : <9100 athlètes
for t in 3..10 do
	for s in 37..20000 do
		link = "http://scoresheet.ffhaltero.fr/scoresheet/search/#{s}/#{t}"
		begin
			page = mechanize.get(link)
			byebug
		rescue
			puts "athlete #{s} KO"
		else
			whole=Nokogiri::HTML(page.body, nil, 'UTF-8')
			xml_doc=Nokogiri::XML(page.body)
		
			table = whole.css('table.open')
			table = whole.at('table')
			rows = whole.xpath("//table/tbody/tr")
			column_names = rows.shift
		
			#On récupère nom et date de naissance
			info = h3.text.strip
			name, date_naissance = info.split('-').map(&:strip)
			puts name
		
			html_txt=whole.to_s
		
			i=0
			table.search('tr').each do |tr|
				if i==0 && s==37 && t==3
					text_csv[0]="Nom"
					text_csv[1]="Date Naissance"
				else
					text_csv[0]=name
					text_csv[1]=date_naissance
				end
			
				cells = tr.search('th, td')
				csv_line=CSV.generate_line(cells)
			
				j=2
				cells.each do |cell|
					text = cell.text.strip
					text_csv[j]=text
					j=j+1
				end
			 
				if s==37 || i!=0 || t==3
					text_out=CSV.generate_line(text_csv)
					File.open(output_path, 'a+') {|f| f.write(text_out)}
				end
			 	i=i+1
			 	# output cell data
			end
		
	
		end
	
	end	
end

File.open("Joris/PycharmProjects/halterodata/haltero_data_full.csv", 'w') { |file| file.write(stuff) }
	
