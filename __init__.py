#  ***** BEGIN GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  The Original Code is Copyright (C) 2017 maximmaxim345
#  All rights reserved.
#
#  ***** END GPL LICENSE BLOCK *****
import bpy, sys, os, time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from splinter import Browser

bl_info = {
	"name": "sheepit",
	"description": "Addon for uploading your project to sheepIt",
	"author": "Maxim Raznatovski",
	"version": (0, 1),
	"blender": (2, 78, 0),
	"location": "Propertys > Render",
	"warning": "Early alpha",
	"support": "TESTING",
	"category": "Render"
}

class SheepitPropertys(bpy.types.PropertyGroup):
	version_options = [
		("blender278c", "2.78c", '', 'BLENDER', 0),
		("blender278c-filmic", "2.78c Filmic", '', 'BLENDER', 1),
		("blender277a", "2.77a", '', 'BLENDER', 2),
		("blender276b", "2.76b", '', 'BLENDER', 3),
		("blender275a", "2.75a", '', 'BLENDER', 4),
		("blender274", "2.74", '', 'BLENDER', 5),
		("blender273a", "2.73a", '', 'BLENDER', 6),
		("blender272b", "2.72b", '', 'BLENDER', 7),
		("blender271", "2.71", '', 'BLENDER', 8),
		("blender270a", "2.70a", '', 'BLENDER', 9),
		("blender269", "2.69", '', 'BLENDER', 10),
		("blender268a", "2.68a", '', 'BLENDER', 11),
		("blender267b", "2.67b", '', 'BLENDER', 12),
		("blender266a", "2.66a", '', 'BLENDER', 13),
		("blender265a", "2.65a", '', 'BLENDER', 14)
	]
	Version = bpy.props.EnumProperty(
		items=version_options,
		description="Executable to use",
		default="blender278c"
	)
	Renderable_by_all_members = bpy.props.BoolProperty(
	name="renderable by all members",
	description = "By default every members can render your project. If you want to restrict the access to your project do not check this box. On the project administration page will be able to modify this settings and add specific members to renderers",
	default = True
	)
	RenderMode = bpy.props.EnumProperty(
	name = "Rendering mode",
	description = "Chose rendering mode",
	items = [("singleframe", "Single Frame", "Render only one Frame"),
			("animation", "Animation", "Render Animation")
			]
	)
	stillSplitting = bpy.props.IntProperty(
	min=4,
	max=64,
	name="Split in tiles",
	description="To increase the render time alowed by frame you can split each frame in tiles. Tiles will act as layers and be put in top of each other to create the final frame. You are allow of 25 min per tile."
	)
	animationSplitting = bpy.props.IntProperty(
	min=1,
	max=64,
	description="To increase the render time alowed by frame you can split each frame in tiles. Tiles will act as layers and be put in top of each other to create the final frame. You are allow of 25 min per tile."
	)
	sendProject=bpy.props.BoolProperty(
	name="Send Project",
	description="Send Project to the Renderfarm"
	)

class sendProject(bpy.types.Operator):
	bl_label = "Send Project"
	bl_idname = "sheepit.send"
	
	def execute(self, context):
		send(self)
		return {"FINISHED"}
class editLogin(bpy.types.Operator):
	bl_label = "Edit cridentials"
	bl_idname = "sheepit.editlogin"
	
	signIn_login = bpy.props.StringProperty(
	name="username",
	description="Username"
	)
	
	signIn_password = bpy.props.StringProperty(
	name="password",
	description="Password",
	subtype="PASSWORD"
	)
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def execute(self, context):
		self.report({'INFO'}, "saved")
		saveLogin(self.signIn_login, self.signIn_password)
		return {"FINISHED"}
	def draw(self, context):
		layout = self.layout
		layout.prop(self, "signIn_login")
		layout.prop(self, "signIn_password")

class sheepItAddon(bpy.types.Panel):
	bl_label = "SheepIt! renderfarm"
	bl_idname = "SHEEP_IT"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "render"
	
	def draw(self, context):
		layout = self.layout
		scene = context.scene
		column = layout.column()
		column.label(text="Settings:")
		column.prop(scene.sheepIt, "Version")
		column.prop(scene.sheepIt, "Renderable_by_all_members")
		row = column.row()
		row.prop(scene.sheepIt, "RenderMode", expand=True)
		if scene.sheepIt.RenderMode == "singleframe":
			column.prop(scene, "frame_current", text="Frame")
			column.prop(scene.sheepIt, "stillSplitting", slider=True)
		else:
			column.prop(scene, "frame_start")
			column.prop(scene, "frame_end")
			column.prop(scene.sheepIt, "animationSplitting", slider=True)
		layout.operator("sheepit.send")
class sheepIt_preferences(bpy.types.AddonPreferences):
	bl_idname = __name__
	def draw(self, context):
		layout = self.layout
		scene = context.scene
		layout.operator("sheepIt.editlogin")
def saveLogin(username, password):
	with open(os.path.join(os.path.dirname( __file__ ), '..', '..', "presets/sheepit.config"), "w") as f:
		f.write(username + "\n" + password)
def getLogin():
	with open(os.path.join(os.path.dirname( __file__ ), '..', '..', "presets/sheepit.config"), "r") as f:
		login = f.read().split("\n")
		return login[0], login[1]
def send(self):
	
	pjsname = "phantomjs-win.exe"
	pjspath = os.path.dirname(os.path.abspath(__file__))+ "\\" + pjsname

	browser = Browser("phantomjs", executable_path=pjspath, service_log_path="C:\\tmp\\l.log")

	browser.visit("https://www.sheepit-renderfarm.com/index.php")

	Button1 = browser.find_by_css("button.navbar-toggle")
	Button1.first.click()
	time.sleep(1)
	Button2 = browser.find_by_css("a.dropdown-toggle.dropdown-form-toggle")
	Button2.first.click()

	usrname, passwd = getLogin()
	
	usernameField = browser.find_by_id("login-header_login")
	usernameField.type(usrname)

	passwordField = browser.find_by_id("login-header_password")
	passwordField.type(passwd)

	signInButton = browser.find_by_id("login-header_submit")
	signInButton.click()

	time.sleep(1)
	browser.visit("https://www.sheepit-renderfarm.com/jobs.php?mode=add")
	browser.attach_file("addjob_archive", bpy.context.blend_data.filepath)
	
	sendButton = browser.find_by_value("Send this file")
	sendButton.first.click()
	
	exeVersion = browser.find_by_id("addjob_exe")
	exeVersion.first.select(bpy.context.scene.sheepIt.Version);
	
	renderableByAll = browser.find_by_name("public_render")
	if bpy.context.scene.sheepIt.Renderable_by_all_members:
		renderableByAll.check()
	else:
		renderableByAll.uncheck()
	
	browser.choose("addjob_change_type_0", bpy.context.scene.sheepIt.RenderMode)
	if bpy.context.scene.sheepIt.RenderMode=="singleframe":
		browser.execute_script("addjob_split_sample_range_value_0.value = " + str(bpy.context.scene.sheepIt.stillSplitting))
	else:
		browser.execute_script("addjob_split_animation_sample_range_value_0.value = " + str(bpy.context.scene.sheepIt.animationSplitting))
	okButton = browser.find_by_id("addjob_submit_0")
	okButton.first.click()
	
	browser.screenshot(name="network", suffix='.png')
	self.report({'INFO'}, "uploaded")
	browser.quit()
def register():
	bpy.utils.register_module(__name__)
	bpy.types.Scene.sheepIt = bpy.props.PointerProperty(type=SheepitPropertys)
	
def unregister():
	bpy.utils.unregister_module(__name__)
	del bpy.types.Scene.sheepIt
	
if __name__ == "__main__":
	register()