from scrapy import cmdline

name = 'oceanengine'
cmd = 'scrapy crawl {0}'.format(name)
cmdline.execute(cmd.split())


