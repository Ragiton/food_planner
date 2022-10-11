
from email.mime import base
from bs4 import BeautifulSoup as bs
import requests
import requests_cache
import pandas as pd
import re
from datetime import datetime
from dataclasses import dataclass, field

requests_cache.install_cache('sitemap_cache')

userAgentRe = re.compile(r'User-agent: (.+)')
siteMapRe = re.compile(r'Sitemap: (.+)')
disallowRe = re.compile(r'Disallow: /(.*)')

@dataclass
class RecipeLink:
	'''Class for keeping track of links to potential recipes on a website'''
	link: str = None
	valid: bool = False
	lastModified: datetime = None

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.link == other.link
		else:
			return False
	
	def __hash__(self):
		return hash(self.link)

def get_sitemap_url(baseurl):
	siteMapUrl = None
	disallow = []
	userAgent = None

	page = requests.get(baseurl+'robots.txt')
	robotsText = page.text

	for line in robotsText.split('\n'):
		agentMatch = userAgentRe.match(line)
		if agentMatch:
			userAgent = agentMatch.group(1)
			# print('userAgent:', userAgent)
		siteMatch = siteMapRe.match(line)
		if siteMatch:
			siteMapUrl = siteMatch.group(1)
			# print('siteMap:', siteMapUrl)
		disallowMatch = disallowRe.match(line)
		if disallowMatch:
			disallow.append(disallowMatch.group(1))
	# print('disallow:', disallow)
	
	return siteMapUrl
		

def get_sitemap(url):
	page = requests.get(url)
	encoding = page.encoding
	# print(encoding)
	xml = bs(page.text, 'xml')

	return xml


def get_child_sitemaps(xml):
	sitemaps = xml.find_all('sitemap')
	output = []

	for sitemap in sitemaps:
		output.append(sitemap.findNext('loc').text)

	return output


def sitemap_to_dataframe(xml, name='', data=None, verbose=False, baseurl=''):
	name = name.replace(baseurl, '')
	urls = xml.find_all('url')

	linksList = []

	for url in urls:
		locResult = url.findNext("loc")
		if locResult is not None:
			loc = locResult.text.replace(baseurl, '')
		else:
			loc = ''
		
		lastModResult = url.findNext('lastmod')
		if lastModResult is not None:
			lastMod = lastModResult.text
		else:
			lastMod = ''

		if loc != '':
			linksList.append((loc, lastMod, name))
	
	df = pd.DataFrame(linksList, columns=['loc', 'lastMod', 'sitemap'])
	return df

def sitemap_to_set(xml, baseurl=''):
	urls = xml.find_all('url')

	linkSet = set()

	for url in urls:
		locResult = url.findNext("loc")
		if locResult is not None:
			loc = locResult.text.replace(baseurl, '')
		else:
			loc = ''
		
		lastModResult = url.findNext('lastmod')
		if lastModResult is not None:
			lastMod = lastModResult.text
		else:
			lastMod = ''

		if loc != '':
			linkSet.add(RecipeLink(link=loc, lastModified=lastMod))

	return linkSet

def get_recipe_link_list(baseurl):
	xml = get_sitemap(get_sitemap_url(baseurl))

	child_sitemaps = get_child_sitemaps(xml)
	# print(child_sitemaps)

	recipeLinkLists = []
	for sitemap in child_sitemaps:
		if not 'post' in sitemap or 'tag' in sitemap:
			continue

		child_xml = get_sitemap(sitemap)
		# print(child_xml)
		# print part of child xml results (first 100 lines)
		# result = child_xml.prettify().splitlines()
		# print('\n'.join(result[:100]))

		df = sitemap_to_dataframe(child_xml, name=sitemap, baseurl=baseurl)
		# print(df)
		recipeLinkLists.append(df)
	totalDF = pd.concat(recipeLinkLists).reset_index(drop=True)

	# print(totalDF)

	return totalDF['loc'].to_list()

def get_recipe_link_set(baseurl):
	xml = get_sitemap(get_sitemap_url(baseurl))

	child_sitemaps = get_child_sitemaps(xml)
	print(child_sitemaps)

	recipeLinkSet = set()
	for sitemap in child_sitemaps:
		if not 'post' in sitemap or 'tag' in sitemap:
			continue

		child_xml = get_sitemap(sitemap)
		# print(child_xml)
		# print part of child xml results (first 100 lines)
		# result = child_xml.prettify().splitlines()
		# print('\n'.join(result[:100]))

		links = sitemap_to_set(child_xml, baseurl=baseurl)
		print(links)
		recipeLinkSet = recipeLinkSet.union(links)
	print(recipeLinkSet)
	return recipeLinkSet

if __name__ == '__main__':
	baseurl = 'https://minimalistbaker.com/'
	baseurl = 'https://www.noracooks.com/'
	results = get_recipe_link_list(baseurl)
	setResults = get_recipe_link_set(baseurl)
	print('list:', len(results), 'set:', len(setResults))
	print('list:', results[:10], 'set:', setResults.pop())
	