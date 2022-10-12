
from datetime import datetime
from bs4 import BeautifulSoup as bs
import requests
import requests_cache
import re
import sitemaps

import random
import time

import pickle

from dataclasses import dataclass, field

requests_cache.install_cache('test_cache')


def make_throttle_hook(timeoutMin=1.0, timeoutMax=5.0):
	"""Make a request hook function that adds a custom delay for non-cached requests"""

	multiplier = timeoutMax-timeoutMin

	def hook(response, *args, **kwargs):
		if not getattr(response, 'from_cache', False):
			print('sleeping')
			time.sleep(random.random()*multiplier+timeoutMin)
		return response
	return hook

recipes = []


# need to keep track of unit mapping, maybe use pint: https://pint.readthedocs.io/en/stable/
units = {}
units['g'] = 1
units['kg'] = 1000


class Nutrition:
	"""Class for keeping track of nutrition info"""

@dataclass
class Ingredient:
	"""Class for keeping track of an ingredient"""
	amount: float = 0
	unit: str = None
	name: str = None
	notes: str = None

	def __str__(self):
		temp = []
		for attr, value in self.__dict__.items():
			if value is not None:
				temp.append(str(value))
		return ' '.join(temp)


class RecipeStep:
	"""Class for keeping track of recipe steps"""
	description: str
	time: float #min


@dataclass
class Recipe:
	"""Class for keeping track of a recipe"""
	name: str = None
	description: str = None
	ingredients: list[Ingredient] = field(default_factory=list)
	servings: float = None
	servingsUnit: str = None
	author: str = None
	prepTime: float = None #minutes
	cookTime: float = None #minutes
	freezerFriendly: bool = False
	storageTimeLimit: float  = None#days
	steps: list[RecipeStep] = field(default_factory=list)
	notes: str = None
	sourceLink: str = None
	printLink: str = None
	tags: list[str] = field(default_factory=list)

def printRecipe(recipe, depth='summary'):
	"""
	prints recipe data to the console
	
	depth : how much data should be printed
			'summary' = name, author, prepTime, cookTime
	"""
	if(depth=='summary'):
		print(recipe.name, 'by: ', recipe.author, 'prep: ', recipe.prepTime, 'cook: ', recipe.cookTime)
	elif(depth=='ingredients'):
		print(recipe.ingredients)
	else:
		for attr, value in recipe.__dict__.items():
			if attr not in ['ingredients']:
				print(attr,':', value)
		print('Ingredients:')
		if recipe.ingredients is not None and recipe.ingredients is not []:
			for i in recipe.ingredients:
				print('\t', i)

def getRecipeFromPage(recipeUrl):
	"""
	Get recipe info from WPRM (word press recipe maker) site
	"""
	recipePage = requests.get(recipeUrl, hooks={'response': make_throttle_hook()})
	recipeSoup = bs(recipePage.text, 'html.parser').find('div', class_='wprm-recipe')
	if recipeSoup is None:
		return None
	
	testIngredientData = Ingredient()
	recipeData = Recipe()
	recipeData.sourceLink = recipeUrl
	
	#check if this page actually contains recipe data, do this by seeing if there is a link to print the recipe
	printTag = recipeSoup.find('a', class_='wprm-recipe-print', href=True)
	if printTag is None:
		return None
	recipeData.printLink = printTag['href']

	# create mapping between css selector and data it should populate if found
	recipeSelectorMap = {
		'.wprm-recipe-name': recipeData.name,
		'.wprm-recipe-summary': recipeData.description,
		'.wprm-recipe-author': recipeData.author,
		'.wprm-recipe-prep_time': recipeData.prepTime,
		'.wprm-recipe-cook_time': recipeData.cookTime,
		'.wprm-recipe-servings': recipeData.servings,
		'.wprm-recipe-servings-unit': recipeData.servingsUnit,
		'.wprm-recipe-freezer-friendly': recipeData.freezerFriendly,
		'.wprm-recipe-does-it-keep': recipeData.storageTimeLimit,
		'.wprm-recipe-notes': recipeData.notes
		}

	# get all data matching each selector and put it into corresponding variable if it is found
	for selector, var in recipeSelectorMap.items():
		tempData = recipeSoup.select_one(selector)
		if tempData is not None:
			var = tempData.text
	
	# wprm-recipe-container-97936 > div > div.wprm-recipe-header-container > div.wprm-recipe-header-left > h2

	servingsUnit = recipeSoup.select_one('.wprm-recipe-servings-unit')
	if servingsUnit is not None:
		recipeData.servingsUnit = servingsUnit.text.replace('(', '').replace(')', '')
	
	course = recipeSoup.select_one('.wprm-recipe-course')
	if course is not None:
		recipeData.tags += [_.strip() for _ in course.text.split(',')]
	
	cuisine = recipeSoup.select_one('.wprm-recipe-cuisine')
	if cuisine is not None:
		recipeData.tags += [_.strip() for _ in cuisine.text.split(',')]



	# get ingredients
	ingredients = []
	ingredientSoup = recipeSoup.find('div', class_='wprm-recipe-ingredient-group')
	for ingredientItem in ingredientSoup.find_all('li', class_='wprm-recipe-ingredient'):
		amount = ingredientItem.find('span', class_='wprm-recipe-ingredient-amount')
		if amount is not None:
			amount = amount.text
		else:
			amount = 'N/A'
		unit = ingredientItem.find('span', class_='wprm-recipe-ingredient-unit')
		if unit is not None:
			unit = unit.text
		else:
			unit = 'N/A'
		name = ingredientItem.find('span', class_='wprm-recipe-ingredient-name').text
		notes = ingredientItem.find('span', class_='wprm-recipe-ingredient-notes')
		if notes is not None:
			notes = notes.text
		ingredients.append(Ingredient(name, amount, unit, notes))

	recipeData.ingredients = ingredients
	# printRecipe(recipeData, depth='all')
	return recipeData

# start with scraping a recipe and testing stuff out a bit, vegan minimalist baker of course

def scrapeRecipeLinks():
	baseurl = 'https://minimalistbaker.com/'
	starturl = 'recipe-index/?fwp_special-diet=vegan'

	page = requests.get(baseurl + starturl)

	if(page.status_code != 200):
		raise RuntimeError('Failed to load page')

	soup = bs(page.text, 'html.parser')

	articles = soup.find_all('article', class_='post-summary')
	articleLinks = []
	for article in articles:
		link = article.a.get('href')
		# print(link)
		articleLinks.append(link)
	
	return articleLinks


def updateLinks(existingSiteLinks, websites):
	# check for any link updates
	for site in websites:
		links = sitemaps.get_recipe_link_dict(site)
		existingLinks = existingSiteLinks[site]
		newLinks = {k:links[k] for k in links.keys() if k not in existingLinks}
		# save link to new dict if new link data is greater than old link date (smaller date preceeds larger date)
		updateLinks = {k:links[k] for k in links.keys() if links[k][1]>existingLinks[k][1]} 
		for link, value in updateLinks:
			existingLinks[link] = value
		existingLinks.update(newLinks)


if __name__ == '__main__':
	# articleLinks = scrapeRecipeLinks()

	# store list of recipe links in set

	# if link is not recipe, mark it or remove it from set?
	websites = ['https://minimalistbaker.com/', 'https://www.noracooks.com/']
	siteLinks = {}

	# get initial set of links
	for site in websites:
		siteLinks[site] = sitemaps.get_recipe_link_dict(site)


	recipes = []
	recipeCount = 0
	linkCount = 0
	# go through all links and get recipe data
	for website, childLinks in siteLinks.items():
		for pageLink, data in childLinks.items():
			print('getting recipe', recipeCount, 'from link ', linkCount, ':', pageLink)
			linkCount += 1
			# time.sleep(random.random()*4+1) # wait random ammount of time between 1 and 5 seconds
			recipe = getRecipeFromPage(website+pageLink)
			if recipe is not None:
				data[0] = True #recipe is valid
				recipes.append(recipe)
				recipeCount += 1
			else:
				data[0] = False #recipe is not valid
	
	print('Links processed:', linkCount, ' Recipes processed:', recipeCount)
	# store recipes to file

	with open('recipes.pkl','wb') as f:
		pickle.dump(recipes, f)
			
	# mbLinks = sitemaps.get_recipe_link_list('https://minimalistbaker.com/')
	# ncLiinks = sitemaps.get_recipe_link_list('https://www.noracooks.com/')

	# for link in articleLinks:
	# 	print('getting recipe from: ', link)
	# 	recipe = getRecipeFromPage(link)
	# 	if recipe is not None:
	# 		recipes.append(recipe)
	# 	print()

	# print(len(recipes))