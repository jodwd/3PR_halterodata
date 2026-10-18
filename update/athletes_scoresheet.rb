require 'mechanize'
require 'csv'

# ---- Settings ----------------------------------------------------------
OUTPUT_DIR   = "C:/Users/joris/PycharmProjects/3PR_halterodata"
T_RANGE      = 10..10
FIRST_ID     = 37
MAX_ID       = 20_000
THREADS      = 40     # parallel requests; raise carefully if no HTTP errors show up
BATCH        = 200   # IDs fetched in parallel before writing them (in order)
EMPTY_STOP   = 2     # stop a t-loop after this many batches in a row with no athlete
# ------------------------------------------------------------------------

output_path = File.join(OUTPUT_DIR, "haltero_data_full.csv")
if File.exist?(output_path)
  stamp = Time.now.strftime("%d_%m_%Y_%H_%M")
  File.rename(output_path, output_path.sub(".csv", "_#{stamp}.csv"))
end

def new_agent
  Mechanize.new do |a|
    a.max_history  = 0   # don't keep every visited page in memory
    a.open_timeout = 10
    a.read_timeout = 20
  end
end

DATE_RE = %r{\d{2}/\d{2}/\d{4}}

# Collapse newlines, tabs and non-breaking spaces into single spaces
def clean(str)
  str.gsub(/[[:space:]\u00A0]+/, ' ').strip
end

# Returns { name:, date:, header:, rows: } or nil if no athlete
def scrape(agent, s, t)
  url = "https://scoresheet.ffhaltero.fr/scoresheet/search/#{s}/#{t}"
  attempts = 0
  begin
    page = agent.get(url)
  rescue Mechanize::ResponseCodeError => e
    return nil if e.response_code == '404'          # athlete doesn't exist
    attempts += 1
    if attempts < 4 then sleep(2 * attempts); retry end
    warn "athlete #{s} (t=#{t}) HTTP #{e.response_code}"
    return nil
  rescue StandardError => e                         # timeout, connection reset...
    attempts += 1
    if attempts < 4 then sleep(2 * attempts); retry end
    warn "athlete #{s} (t=#{t}) #{e.class}: #{e.message}"
    return nil
  end

  doc = Nokogiri::HTML(page.body, nil, 'UTF-8')

  # The results table is the one with the "Licence" column
  table = doc.css('table').find { |tb| tb.text.include?('Licence') }
  return nil unless table

  # First <h3> is "Recherche" (search box); the athlete's name is the other one
  h3   = doc.css('h3').find { |h| h.text.strip != 'Recherche' }
  name = h3 ? clean(h3.text) : ''

  # Birth date is the first dd/mm/yyyy text after the name
  date = ''
  if h3
    txt  = h3.xpath('following::text()').map(&:text).find { |x| x =~ DATE_RE }
    date = txt[DATE_RE] if txt
  end

  rows = table.search('tr').map { |tr| tr.search('th, td').map { |c| clean(c.text) } }
  { name: name, date: date, header: rows.first, rows: rows.drop(1) }
rescue StandardError => e
  warn "athlete #{s} (t=#{t}) parse error: #{e.class}: #{e.message}"
  nil
end

# Fetch a batch of IDs in parallel, one Mechanize agent per thread
def fetch_batch(agents, ids, t)
  queue = Queue.new
  ids.each { |s| queue << s }
  queue.close

  results = {}
  mutex   = Mutex.new
  agents.map do |agent|
    Thread.new do
      while (s = queue.pop)
        r = scrape(agent, s, t)
        mutex.synchronize { results[s] = r }
      end
    end
  end.each(&:join)
  results
end

agents = Array.new(THREADS) { new_agent }
header_written = false
started = Time.now

CSV.open(output_path, 'w') do |csv|
  T_RANGE.each do |t|
    empty_batches = 0

    (FIRST_ID..MAX_ID).each_slice(BATCH) do |ids|
      results = fetch_batch(agents, ids, t)
      found = 0

      ids.each do |s|                     # write in ID order
        r = results[s]
        unless r
          puts "athlete #{s} KO"
          next
        end
        found += 1
        puts r[:name]

        unless header_written
          csv << ['Nom', 'Date Naissance'] + r[:header]
          header_written = true
        end
        r[:rows].each { |cells| csv << [r[:name], r[:date]] + cells }
      end

      csv.flush                           # saved even if you Ctrl+C
      puts "t=#{t} ids #{ids.first}-#{ids.last}: #{found} athletes (#{(Time.now - started).round}s)"

      empty_batches = found.zero? ? empty_batches + 1 : 0
      break if empty_batches >= EMPTY_STOP
    end
  end
end

puts "Done in #{((Time.now - started) / 60).round(1)} min -> #{output_path}"
