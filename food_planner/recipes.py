
from dataclasses import dataclass, field

import pickle

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
		print(recipe.name, 'by: ', recipe.author, 
			'prep: ', recipe.prepTime, 'cook: ', recipe.cookTime, 
			'numIngredients:', len(recipe.ingredients), 
			'serves:', recipe.servings, recipe.servingsUnit)
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

def loadRecipes(filename='recipes'):
	return pickle.load(filename+'.pkl')

def dumpRecipes(recipesList, filename='recipes'):
	with open(filename+'.pkl','wb') as f:
		pickle.dump(recipesList, f)

if __name__ == '__main__':
	recipes = loadRecipes()

	print('recipes.pkl has ', len(recipes), 'recipes stored')
	print('type:', type(recipes))
	print('first recipe:')
	printRecipe(recipes[0], depth='summary')