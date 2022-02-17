from django.urls import path, include
import food.views as azt_views
import food.utils.view_utils as azt_view_utils

urlpatterns = [
    path('restaurants/', azt_views.RestaurantsView.as_view({'get': 'list'}), name="restaurants_view"),
    path('restaurants/<str:id>/', azt_views.RestaurantsView.as_view({'get': 'retrieve'}), name="restaurant_view"),

    path('categories/', azt_views.CategoriesView.as_view({'get': 'list'}), name="categories_view"),
    path('categories/<str:id>/', azt_views.CategoriesView.as_view({'get': 'retrieve'}), name="category_view"),

]
