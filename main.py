
from datetime import datetime
from bs4 import BeautifulSoup as bs
import requests
import requests_cache
import re
import sitemaps

import random
import time

from dataclasses import dataclass, field

requests_cache.install_cache('test_cache')

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
	recipePage = requests.get(recipeUrl)
	recipeSoup = bs(recipePage.text, 'html.parser').find('div', class_='wprm-recipe')
	if recipeSoup is None:
		return None

	testIngredientData = Ingredient()
	recipeData = Recipe()
	recipeData.sourceLink = recipeUrl
	
	printTag = recipeSoup.find('a', class_='wprm-recipe-print', href=True)
	if printTag is None:
		return None
	recipeData.printLink = printTag['href']
	#wprm-recipe-container-97936 > div > div.wprm-recipe-header-container > div.wprm-recipe-header-left > h2
	recipeData.name = recipeSoup.select_one('.wprm-recipe-name').text
	recipeData.description = recipeSoup.select_one('.wprm-recipe-summary').text
	recipeData.author = recipeSoup.select_one('.wprm-recipe-author').text

	prepTimeTag = recipeSoup.select_one('.wprm-recipe-prep_time')
	if prepTimeTag is not None:
		recipeData.prepTime = prepTimeTag.text
	else:
		recipeData.prepTime = '0'
	
	cookTimeTag = recipeSoup.select_one('.wprm-recipe-cook_time')
	if cookTimeTag is not None:
		recipeData.cookTime = cookTimeTag.text
	else:
		recipeData.cookTime = '0'
	
	recipeData.servings = recipeSoup.select_one('.wprm-recipe-servings').text
	recipeData.servingsUnit = recipeSoup.select_one('.wprm-recipe-servings-unit').text.replace('(', '').replace(')', '')
	recipeData.tags += [_.strip() for _ in recipeSoup.select_one('.wprm-recipe-course').text.split(',')]
	recipeData.tags += [_.strip() for _ in recipeSoup.select_one('.wprm-recipe-cuisine').text.split(',')]
	recipeData.freezerFriendly = recipeSoup.select_one('.wprm-recipe-freezer-friendly').text
	recipeData.storageTimeLimit = recipeSoup.select_one('.wprm-recipe-does-it-keep').text
	recipeData.notes = recipeSoup.select_one('.wprm-recipe-notes').text

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
	printRecipe(recipeData, depth='all')
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





if __name__ == '__main__':
	# articleLinks = scrapeRecipeLinks()

	# store list of recipe links in set

	# if link is not recipe, mark it or remove it from set?
	websites = ['https://minimalistbaker.com/', 'https://www.noracooks.com/']
	siteLinks = {}

	# get initial set of links
	for site in websites:
		siteLinks[site] = sitemaps.get_recipe_link_set(site)

	# check for any link updates
	for site in websites:
		links = sitemaps.get_recipe_link_set(site)
		existingLinks = siteLinks[site]
		newLinks = links.difference(existingLinks)
		updateLinks = links.difference(newLinks)
		for link in updateLinks:
			if link.lastModified > existingLinks
			
	# mbLinks = sitemaps.get_recipe_link_list('https://minimalistbaker.com/')
	# ncLiinks = sitemaps.get_recipe_link_list('https://www.noracooks.com/')

	# for link in articleLinks:
	# 	print('getting recipe from: ', link)
	# 	recipe = getRecipeFromPage(link)
	# 	if recipe is not None:
	# 		recipes.append(recipe)
	# 	print()

	# print(len(recipes))