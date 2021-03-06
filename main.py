import os, webapp2, jinja2, re
from string import letters
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
								autoescape = True)

def render_str(template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		return render_str(template, **params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

########## Blog #################
def blog_key(name = 'default'):
	return db.Key.from_path('blogs', name)

class Entry(db.Model):
	title = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)

	def render(self):
		self._render_text = self.content.replace('\n', '</p><p>')
		return render_str("entry.html", e = self)

class Blog(Handler):
	def get(self):
		entries = db.GqlQuery("SELECT * FROM Entry ORDER BY created DESC LIMIT 10")
		self.render("blog-home.html", entries = entries)

class EntryPage(Handler):
	def get(self, entry_id):
		key = db.Key.from_path('Entry', int(entry_id), parent=blog_key())
		entry = db.get(key)

		if not entry:
			self.error(404)
			return

		self.render("permalink.html", entry = entry)

class NewEntry(Handler):
	def get(self):
		self.render("new-entry.html")

	def post(self):
		title = self.request.get("title")
		content = self.request.get("content")
		code = self.request.get("code")

		if title and content:
			if code == "put_your_own_code_here":
				e = Entry(parent = blog_key(), title = title, content = content)
				e.put()
				self.redirect('/blog/%s' % str(e.key().id()))
			else:
				error = "?"
				self.render("new-entry.html", title=title, content=content, error = error)
		else:
			error = "You need a title and some content"
			self.render("new-entry.html", title=title, content=content, error = error)

########## Home #################
class Home(Handler):
	def get(self):
		entries = db.GqlQuery("SELECT * FROM Entry ORDER BY created DESC LIMIT 1")
		self.render("index.html", entries = entries)

########## Code #################
class Code(Handler):
	def get(self):
		self.render("code.html")

########## Fun #################
class Fun(Handler):
	def get(self):
		self.render("fun.html")

########## Resources #################
class Resources(Handler):
	def get(self):
		self.render("resources.html")

#Routes
app = webapp2.WSGIApplication([	('/?', Home),
								('/blog', Blog), 
								('/blog/([0-9]+)', EntryPage), 
								('/blog/write', NewEntry),
								('/code', Code), 
								('/fun', Fun), 
								('/resources', Resources), 
								],
								 debug = True)