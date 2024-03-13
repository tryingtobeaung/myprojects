from love.models import CategoryModel

def allCategory(request):
    category = CategoryModel.objects.all()
    return{'category':category}