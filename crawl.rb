require 'anemone'
require 'sqlite'

Anemone.crawl("http://avloppsguiden.se") do |anemone|
  anemone.on_every_page do |page|
      puts page.url
      anemone.storage = Anemone::Storage.PStore
  end
end
