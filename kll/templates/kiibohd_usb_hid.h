/* Copyright (C) 2018 by Jacob Alexander
 *
 * This file is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This file is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this file.  If not, see <http://www.gnu.org/licenses/>.
 */

<|Information|>

// Refer to https://github.com/hid-io/layouts for specific details
// Generated using https://github.com/hid-io/layouts-python


#pragma once

// ----- Defines -----

// Keyboard + Keypad
<|USBCDefineKeyboardMapping|>


// LED Indicators
<|USBCDefineLEDMapping|>


// Mouse Buttons - USB HID 1.12v2 pg 67
// XXX (HaaTa): Not currently generated by hid-io/layouts
#define MOUSE_NOPRESS      0x00
#define MOUSE_PRIMARY      0x01 // Button 1
#define MOUSE_SECONDARY    0x02 // Button 2
#define MOUSE_TERTIARY     0x03 // Button 3
#define MOUSE_BUTTON(x)       x
// Continues to 0xFFFF, the higher the Mouse code, the selector significance descreases
// Buttons can be defined as:
//  Sel - Selector
//  OOC - On/Off Control
//  MC  - Momentary Control
//  OSC - One-Shot Control
// depending on context.


// System Control
<|USBCDefineSystemControlMapping|>


// Consumer Control
<|USBCDefineConsumerControlMapping|>
