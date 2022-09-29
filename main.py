

import string
from bs4 import BeautifulSoup as bs
import requests
import re

from dataclasses import dataclass



recipes = {}


# need to keep track of unit mapping
units = {}
units['g'] = 1
units['kg'] = 1000
units['']

@dataclass
class Nutrition:
	"""Class for keeping track of nutrition info"""

@dataclass
class Ingredient:
	"""Class for keeping track of an ingredient"""
	name: str
	amount: float = 0

@dataclass
class RecipeStep:
	"""Class for keeping track of recipe steps"""
	description: str
	time: float #min


@dataclass
class Recipe:
	"""Class for keeping track of a recipe"""
	ingredients: list[Ingredient]
	servings: float
	author: str
	prepTime: float #minutes
	cookTime: float #minutes
	freezerFriendly: bool
	storageTimeLimit: float #days
	steps: list[RecipeStep]
	notes: str



