from django.db import models

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

# 4. Modello Pianificazione Settimanale (Cosa cuciniamo e quando?)
class WeeklyPlan(models.Model):
    DAY_CHOICES = [
        ('MON', 'Lunedì'), ('TUE', 'Martedì'), ('WED', 'Mercoledì'),
        ('THU', 'Giovedì'), ('FRI', 'Venerdì'), ('SAT', 'Sabato'), ('SUN', 'Domenica'),
    ]
    MEAL_CHOICES = [
        ('LUN', 'Pranzo'), ('DIN', 'Cena'), ('BRK', 'Colazione'), ('SNK', 'Snack'),
    ]
    
    # Useremo solo il giorno della settimana e il tipo di pasto per semplicità iniziale
    # In una versione avanzata useresti una data per tracciare settimane specifiche
    
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name="Ricetta Scelta")
    day_of_week = models.CharField(max_length=3, choices=DAY_CHOICES, verbose_name="Giorno")
    meal_type = models.CharField(max_length=3, choices=MEAL_CHOICES, verbose_name="Tipo Pasto")
    
    class Meta:
        # Ordiniamo il piano per giorno della settimana per una visualizzazione logica
        ordering = ['day_of_week', 'meal_type'] 
        verbose_name = "Pianificazione Settimanale"
        verbose_name_plural = "Pianificazioni Settimanali"

    def __str__(self):
        return f"{self.get_day_of_week_display()} - {self.get_meal_type_display()}: {self.recipe.name}"