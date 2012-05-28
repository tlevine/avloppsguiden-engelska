#!/usr/bin/env/ruby

require 'anemone'

Anemone.crawl("http://avloppsguiden.se") do |anemone|
  anemone.on_every_page do |page|
      puts page.url
      anemone.storage = Anemone::Storage.MongoDB
  end
end
