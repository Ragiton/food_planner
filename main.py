

from email.mime import base
import string
from tracemalloc import start
from bs4 import BeautifulSoup as bs
import requests
import requests_cache
import re

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
	source: str = None
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
		if ingredients is not None and ingredients is not []:
			for i in ingredients:
				print('\t', i)


# start with scraping a recipe and testing stuff out a bit, vegan minimalist baker of course

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
	print(link)
	articleLinks.append(link)

pageRecipe = requests.get(articleLinks[0])
soupRecipe = bs(pageRecipe.text, 'html.parser')

testIngredientData = Ingredient()
testRecipeStep = RecipeStep()
testRecipeData = Recipe()
#wprm-recipe-container-97936 > div > div.wprm-recipe-header-container > div.wprm-recipe-header-left > h2
recipeSoup = soupRecipe.find('div', class_='wprm-recipe')
testRecipeData.name = recipeSoup.select_one('.wprm-recipe-name').text
testRecipeData.description = recipeSoup.select_one('.wprm-recipe-summary').text
testRecipeData.author = recipeSoup.select_one('.wprm-recipe-author').text
testRecipeData.prepTime = recipeSoup.select_one('.wprm-recipe-prep_time').text
testRecipeData.cookTime = recipeSoup.select_one('.wprm-recipe-cook_time').text
testRecipeData.servings = recipeSoup.select_one('.wprm-recipe-servings').text
testRecipeData.servingsUnit = recipeSoup.select_one('.wprm-recipe-servings-unit').text
testRecipeData.tags += [_.strip() for _ in recipeSoup.select_one('.wprm-recipe-course').text.split(',')]
testRecipeData.tags += [_.strip() for _ in recipeSoup.select_one('.wprm-recipe-cuisine').text.split(',')]
testRecipeData.freezerFriendly = recipeSoup.select_one('.wprm-recipe-freezer-friendly').text
testRecipeData.storageTimeLimit = recipeSoup.select_one('.wprm-recipe-does-it-keep').text

# get ingredients
ingredients = []
ingredientSoup = recipeSoup.find('div', class_='wprm-recipe-ingredient-group')
for ingredientItem in ingredientSoup.find_all('li', class_='wprm-recipe-ingredient'):
	amount = ingredientItem.find('span', class_='wprm-recipe-ingredient-amount').text
	unit = ingredientItem.find('span', class_='wprm-recipe-ingredient-unit').text
	name = ingredientItem.find('span', class_='wprm-recipe-ingredient-name').text
	notes = ingredientItem.find('span', class_='wprm-recipe-ingredient-notes')
	if notes is not None:
		notes = notes.text
	ingredients.append(Ingredient(name, amount, unit, notes))

testRecipeData.ingredients = ingredients
printRecipe(testRecipeData, depth='all')
# print(soup.prettify())