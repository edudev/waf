#!/usr/bin/env python
# encoding: utf-8

from waflib import Task, Node, Utils, Errors
from waflib.TaskGen import extension

class glsl(Task.Task):
	"""
	Task to compile glsl files.
	"""

	def run(self):
		variableFormat = self.env.VARIABLE
		if not variableFormat:
			raise Errors.WafError('Unable to find a variable format string for glsl!')

		for index in range(len(self.inputs)):
			src_node = self.inputs[index]
			bld_node = self.outputs[index]

			# create output dirs if non-existant
			bld_node.parent.mkdir()

			# deduce variable name from pattern or use predefined one
			variableName = Utils.subst_vars(variableFormat, self.env)

			# start writing the string
			bld_node.write('char* ' + variableName + ' = "')

			for line in src_node.read().splitlines():
				# escape '\' and '"'
				line = line.replace("\\", "\\\\")
				line = line.replace("\"", "\\\"")

				# if line isn't a comment, append it to the string
				if not line.startswith(('/*',' *','//')):
					bld_node.write(line.strip(), flags='a')

			# close the string
			bld_node.write('";', flags='a')

		return 0

@extension('.glslv', '.glslf')
def glsl_file(self, node):
	"""
	Compile a glsl file and bind the task to *self.glsltask*. If an existing glsl task is already set, add the node
	to its inputs.

	:param node: glsl file
	:type node: :py:class:`waflib.Node.Node`
	"""

	# Do we need only one glsl task? Having multiple will speed up re-builds
	"""
	glsltask = getattr(self, "glsltask", None)

	if not glsltask:
		glsltask = self.create_task('glsl')
		self.glsltask = glsltask # this assumes one glsl task by task generator
		glsltask.name = self.name
		glsltask.target = self.target
	"""
	glsltask = self.create_task('glsl')
	glsltask.name = self.name
	glsltask.target = self.target

	# change output extension
	extension = node.suffix();
	c_node = node.change_ext(extension + '.c')

	# append nodes to task
	glsltask.inputs.append(node)
	glsltask.outputs.append(c_node)

	# append the output node to sources in order for waf to pick it up
	# perhaps this should be done only if a C compiler is available...
	self.source.append(c_node)
