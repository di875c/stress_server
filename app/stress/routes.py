from app.stress import views

# настраиваем пути, которые будут вести к нашей странице
def setup_routes(app):
   app.router.add_get("/", views.index)
   app.router.add_get("/cross_section", views.section_analysis)
   # app.router.add_post("/db", views.db_post)
   app.router.add_route('*', "/db", views.DbView)