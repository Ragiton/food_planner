

from email.mime import base
import string
from tracemalloc import start
from bs4 import BeautifulSoup as bs
import requests
import re

from dataclasses import dataclass



recipes = {}


# need to keep track of unit mapping, maybe use pint: https://pint.readthedocs.io/en/stable/
units = {}
units['g'] = 1
units['kg'] = 1000


class Nutrition:
	"""Class for keeping track of nutrition info"""


class Ingredient:
	"""Class for keeping track of an ingredient"""
	name: str
	amount: float = 0


class RecipeStep:
	"""Class for keeping track of recipe steps"""
	description: str
	time: float #min



class Recipe:
	"""Class for keeping track of a recipe"""
	name: str
	description: str
	ingredients: list[Ingredient] = []
	servings: float
	servingsUnit: str
	author: str
	prepTime: float #minutes
	cookTime: float #minutes
	freezerFriendly: bool
	storageTimeLimit: float #days
	steps: list[RecipeStep] = []
	notes: str
	source: str
	tags: list[str] = []

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
			print(attr, value)


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
recipeDiv = soupRecipe.find('div', class_='wprm-recipe')
testRecipeData.name = recipeDiv.select_one('.wprm-recipe-name').text
testRecipeData.description = recipeDiv.select_one('.wprm-recipe-summary').text
testRecipeData.author = recipeDiv.select_one('.wprm-recipe-author').text
testRecipeData.prepTime = recipeDiv.select_one('.wprm-recipe-prep_time').text
testRecipeData.cookTime = recipeDiv.select_one('.wprm-recipe-cook_time').text
testRecipeData.servings = recipeDiv.select_one('.wprm-recipe-servings').text
testRecipeData.servingsUnit = recipeDiv.select_one('.wprm-recipe-servings-unit').text
testRecipeData.tags += [_.strip() for _ in recipeDiv.select_one('.wprm-recipe-course').text.split(',')]
testRecipeData.tags += [_.strip() for _ in recipeDiv.select_one('.wprm-recipe-cuisine').text.split(',')]
testRecipeData.freezerFriendly = recipeDiv.select_one('.wprm-recipe-freezer-friendly').text
testRecipeData.storageTimeLimit = recipeDiv.select_one('.wprm-recipe-does-it-keep').text

printRecipe(testRecipeData, depth='all')
# print(soup.prettify())