from django.db import models

# Definizione delle Choices (utilizzate in MealSlot)
DAY_CHOICES = [
    ('MON', 'Lunedì'), ('TUE', 'Martedì'), ('WED', 'Mercoledì'),
    ('THU', 'Giovedì'), ('FRI', 'Venerdì'), ('SAT', 'Sabato'), ('SUN', 'Domenica'),
]
MEAL_TYPE_CHOICES = [
    ('LUN', 'Pranzo'), ('DIN', 'Cena'), ('BRK', 'Colazione'), ('SNK', 'Snack'),
]

# 1. Modello Ingrediente (Cosa compriamo?)
class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome Ingrediente")
    unit = models.CharField(max_length=50, verbose_name="Unità di Misura (es: g, ml, pezzi)")

    def __str__(self):
        return f"{self.name} ({self.unit})"

# 2. Modello Ricetta (Nome del piatto)
class Recipe(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Nome Ricetta")

    def __str__(self):
        return self.name

# 3. Modello Dettaglio Ricetta (Quanti e quali ingredienti servono?)
class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients_list', verbose_name="Ricetta")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, verbose_name="Ingrediente")
    quantity = models.FloatField(verbose_name="Quantità")

    class Meta:
        # Assicura che un ingrediente sia elencato una sola volta per ricetta
        unique_together = ('recipe', 'ingredient')

    def __str__(self):
        return f"{self.recipe.name}: {self.quantity} {self.ingredient.unit} di {self.ingredient.name}"

# --------------------------------------------------------
# 4. NUOVI MODELLI PER PIANIFICAZIONE MULTI-RICETTA
# --------------------------------------------------------

class MealSlot(models.Model):
    """
    Rappresenta un singolo slot pasto nella griglia settimanale (es. Lunedì - Cena).
    È il CONTENITORE per una o più ricette.
    """
    day = models.CharField(max_length=3, choices=DAY_CHOICES, verbose_name="Giorno")
    meal_type = models.CharField(max_length=3, choices=MEAL_TYPE_CHOICES, verbose_name="Tipo Pasto")

    class Meta:
        # Garantisce che ci sia un solo slot pasto per giorno/tipo (es. una sola "Lunedì - Cena")
        unique_together = ('day', 'meal_type')
        ordering = ['day', 'meal_type']
        verbose_name = "Slot Pasto"
        verbose_name_plural = "Slot Pasti"

    def __str__(self):
        return f"{self.get_day_display()} - {self.get_meal_type_display()}"


class MealRecipe(models.Model):
    """
    Collega una specifica ricetta a un MealSlot.
    Questo permette l'associazione di molte ricette a un unico slot (uno slot a molte ricette).
    """
    # Lo slot a cui è assegnata questa ricetta
    meal_slot = models.ForeignKey(
        MealSlot, 
        related_name='recipes', 
        on_delete=models.CASCADE,
        verbose_name="Slot Pasto"
    )
    # La ricetta che fa parte di questo slot
    recipe = models.ForeignKey(
        Recipe, 
        on_delete=models.CASCADE,
        verbose_name="Ricetta Scelta"
    )
    
    # Campo opzionale per ordinare (es. 1=Primo, 2=Secondo, 3=Dolce)
    # order = models.PositiveSmallIntegerField(default=0, verbose_name="Ordine nel Pasto")

    class Meta:
        # Aggiunge un vincolo: una ricetta non può essere aggiunta due volte allo stesso slot
        unique_together = ('meal_slot', 'recipe')
        ordering = ['meal_slot', 'id']
        verbose_name = "Ricetta nel Pasto"
        verbose_name_plural = "Ricette nel Pasto"

    def __str__(self):
        return f"{self.recipe.name} in {self.meal_slot}"