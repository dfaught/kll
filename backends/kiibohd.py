#!/usr/bin/env python3
# KLL Compiler - Kiibohd Backend
#
# Backend code generator for the Kiibohd Controller firmware.
#
# Copyright (C) 2014 by Jacob Alexander
#
# This file is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this file.  If not, see <http://www.gnu.org/licenses/>.

### Imports ###

import os
import sys
import re

# Modifying Python Path, which is dumb, but the only way to import up one directory...
sys.path.append( os.path.expanduser('..') )

from kll_lib.containers import *


### Decorators ###

 ## Print Decorator Variables
ERROR = '\033[5;1;31mERROR\033[0m:'



### Classes ###

class Backend:
	# Initializes backend
	# Looks for template file and builds list of fill tags
	def __init__( self, templatePath ):
		# Does template exist?
		if not os.path.isfile( templatePath ):
			print ( "{0} '{1}' does not exist...".format( ERROR, templatePath ) )
			sys.exit( 1 )

		self.templatePath = templatePath
		self.fill_dict = dict()

		# Generate list of fill tags
		self.tagList = []
		with open( templatePath, 'r' ) as openFile:
			for line in openFile:
				match = re.findall( '<\|([^|>]+)\|>', line )
				for item in match:
					self.tagList.append( item )


	# USB Code Capability Name
	def usbCodeCapability( self ):
		return "usbKeyOut";


	# Processes content for fill tags and does any needed dataset calculations
	def process( self, capabilities, macros ):
		## Capabilities ##
		self.fill_dict['CapabilitiesList'] = "const Capability CapabilitiesList[] = {\n"

		# Keys are pre-sorted
		for key in capabilities.keys():
			funcName = capabilities.funcName( key )
			argByteWidth = capabilities.totalArgBytes( key )
			self.fill_dict['CapabilitiesList'] += "\t{{ {0}, {1} }},\n".format( funcName, argByteWidth )

		self.fill_dict['CapabilitiesList'] += "};"


		## Results Macros ##
		self.fill_dict['ResultMacros'] = ""

		# Iterate through each of the result macros
		for result in range( 0, len( macros.resultsIndexSorted ) ):
			self.fill_dict['ResultMacros'] += "Guide_RM( {0} ) = {{ ".format( result )

			# Add the result macro capability index guide (including capability arguments)
			# See kiibohd controller Macros/PartialMap/kll.h for exact formatting details
			for sequence in range( 0, len( macros.resultsIndexSorted[ result ] ) ):
				# For each combo in the sequence, add the length of the combo
				self.fill_dict['ResultMacros'] += "{0}, ".format( len( macros.resultsIndexSorted[ result ][ sequence ] ) )

				# For each combo, add each of the capabilities used and their arguments
				for combo in range( 0, len( macros.resultsIndexSorted[ result ][ sequence ] ) ):
					resultItem = macros.resultsIndexSorted[ result ][ sequence ][ combo ]

					# Add the capability index
					self.fill_dict['ResultMacros'] += "{0}, ".format( capabilities.getIndex( resultItem[0] ) )

					# Add each of the arguments of the capability
					for arg in range( 0, len( resultItem[1] ) ):
						self.fill_dict['ResultMacros'] += "0x{0:02X}, ".format( resultItem[1][ arg ] )

			# Add list ending 0 and end of list
			self.fill_dict['ResultMacros'] += "0 };\n"
		self.fill_dict['ResultMacros'] = self.fill_dict['ResultMacros'][:-1] # Remove last newline


		## Result Macro List ##
		self.fill_dict['ResultMacroList'] = "ResultMacro ResultMacroList[] = {\n"

		# Iterate through each of the result macros
		for result in range( 0, len( macros.resultsIndexSorted ) ):
			self.fill_dict['ResultMacroList'] += "\tDefine_RM( {0} ),\n".format( result )
		self.fill_dict['ResultMacroList'] += "};"


		## Trigger Macros ##
		self.fill_dict['TriggerMacros'] = ""

		# Iterate through each of the trigger macros
		for trigger in range( 0, len( macros.triggersIndexSorted ) ):
			self.fill_dict['TriggerMacros'] += "Guide_TM( {0} ) = {{ ".format( trigger )

			# Add the trigger macro scan code guide
			# See kiibohd controller Macros/PartialMap/kll.h for exact formatting details
			for sequence in range( 0, len( macros.triggersIndexSorted[ trigger ][ 0 ] ) ):
				# For each combo in the sequence, add the length of the combo
				self.fill_dict['TriggerMacros'] += "{0}, ".format( len( macros.triggersIndexSorted[ trigger ][0][ sequence ] ) )

				# For each combo, add the key type, key state and scan code
				for combo in range( 0, len( macros.triggersIndexSorted[ trigger ][ 0 ][ sequence ] ) ):
					triggerItem = macros.triggersIndexSorted[ trigger ][ 0 ][ sequence ][ combo ]

					# TODO Add support for Analog keys
					# TODO Add support for LED states
					self.fill_dict['TriggerMacros'] += "0x00, 0x01, 0x{0:02X}, ".format( triggerItem )

			# Add list ending 0 and end of list
			self.fill_dict['TriggerMacros'] += "0 };\n"
		self.fill_dict['TriggerMacros'] = self.fill_dict['TriggerMacros'][ :-1 ] # Remove last newline


		## Trigger Macro List ##
		self.fill_dict['TriggerMacroList'] = "TriggerMacro TriggerMacroList[] = {\n"

		# Iterate through each of the trigger macros
		for trigger in range( 0, len( macros.triggersIndexSorted ) ):
			# Use TriggerMacro Index, and the corresponding ResultMacro Index
			self.fill_dict['TriggerMacroList'] += "\tDefine_TM( {0}, {1} ),\n".format( trigger, macros.triggersIndexSorted[ trigger ][1] )
		self.fill_dict['TriggerMacroList'] += "};"


		## Max Scan Code ##
		self.fill_dict['MaxScanCode'] = "#define MaxScanCode 0x{0:X}".format( macros.overallMaxScanCode )


		## Default Layer and Default Layer Scan Map ##
		self.fill_dict['DefaultLayerTriggerList'] = ""
		self.fill_dict['DefaultLayerScanMap'] = "const unsigned int *default_scanMap[] = {\n"

		# Iterate over triggerList and generate a C trigger array for the default map and default map array
		for triggerList in range( 0, len( macros.triggerList[ 0 ] ) ):
			# Generate ScanCode index and triggerList length
			self.fill_dict['DefaultLayerTriggerList'] += "Define_TL( default, 0x{0:02X} ) = {{ {1}".format( triggerList, len( macros.triggerList[ 0 ][ triggerList ] ) )

			# Add scanCode trigger list to Default Layer Scan Map
			self.fill_dict['DefaultLayerScanMap'] += "default_tl_0x{0:02X}, ".format( triggerList )

			# Add each item of the trigger list
			for trigger in macros.triggerList[ 0 ][ triggerList ]:
				self.fill_dict['DefaultLayerTriggerList'] += ", {0}".format( trigger )

			self.fill_dict['DefaultLayerTriggerList'] += " };\n"
		self.fill_dict['DefaultLayerTriggerList'] = self.fill_dict['DefaultLayerTriggerList'][:-1] # Remove last newline
		self.fill_dict['DefaultLayerScanMap'] = self.fill_dict['DefaultLayerScanMap'][:-2] # Remove last comma and space
		self.fill_dict['DefaultLayerScanMap'] += "\n};"


		## Partial Layers and Partial Layer Scan Maps ##
		self.fill_dict['PartialLayerTriggerLists'] = ""
		self.fill_dict['PartialLayerScanMaps'] = ""

		# Iterate over each of the layers, excluding the default layer
		for layer in range( 1, len( macros.triggerList ) ):
			# Prepare each layer
			self.fill_dict['PartialLayerScanMaps'] += "// Partial Layer {0}\n".format( layer )
			self.fill_dict['PartialLayerScanMaps'] += "const unsigned int *layer{0}_scanMap[] = {{\n".format( layer )
			self.fill_dict['PartialLayerTriggerLists'] += "// Partial Layer {0}\n".format( layer )

			# Iterate over triggerList and generate a C trigger array for the layer
			for triggerList in range( 0, len( macros.triggerList[ layer ] ) ):
				# Generate ScanCode index and triggerList length
				self.fill_dict['PartialLayerTriggerLists'] += "Define_TL( layer{0}, 0x{1:02X} ) = {{ {2}".format( layer, triggerList, len( macros.triggerList[ layer ][ triggerList ] ) )

				# Add scanCode trigger list to Default Layer Scan Map
				self.fill_dict['PartialLayerScanMaps'] += "layer{0}_tl_0x{1:02X}, ".format( layer, triggerList )

				# Add each item of the trigger list
				for trigger in macros.triggerList[ layer ][ triggerList ]:
					self.fill_dict['PartialLayerTriggerLists'] += ", {0}".format( trigger )

				self.fill_dict['PartialLayerTriggerLists'] += " };\n"
			self.fill_dict['PartialLayerTriggerLists'] += "\n"
			self.fill_dict['PartialLayerScanMaps'] = self.fill_dict['PartialLayerScanMaps'][:-2] # Remove last comma and space
			self.fill_dict['PartialLayerScanMaps'] += "\n};\n\n"
		self.fill_dict['PartialLayerTriggerLists'] = self.fill_dict['PartialLayerTriggerLists'][:-2] # Remove last 2 newlines
		self.fill_dict['PartialLayerScanMaps'] = self.fill_dict['PartialLayerScanMaps'][:-2] # Remove last 2 newlines


		## Layer Index List ##
		self.fill_dict['LayerIndexList'] = "Layer LayerIndex[] = {\n"

		# Iterate over each layer, adding it to the list
		for layer in range( 0, len( macros.triggerList ) ):
			# Default map is a special case, always the first index
			# TODO Fix names
			if layer == 0:
				self.fill_dict['LayerIndexList'] += '\tLayer_IN( default_scanMap, "DefaultMap" ),\n'
			else:
				self.fill_dict['LayerIndexList'] += '\tLayer_IN( layer{0}_scanMap, "Layer {0}" ),\n'.format( layer )
		self.fill_dict['LayerIndexList'] += "};"


	# Generates the output keymap with fill tags filled
	def generate( self, filepath ):
		# Process each line of the template, outputting to the target path
		with open( filepath, 'w' ) as outputFile:
			with open( self.templatePath, 'r' ) as templateFile:
				for line in templateFile:
					# TODO Support multiple replacements per line
					# TODO Support replacement with other text inline
					match = re.findall( '<\|([^|>]+)\|>', line )

					# If match, replace with processed variable
					if match:
						outputFile.write( self.fill_dict[ match[ 0 ] ] )
						outputFile.write("\n")

					# Otherwise, just append template to output file
					else:
						outputFile.write( line )
