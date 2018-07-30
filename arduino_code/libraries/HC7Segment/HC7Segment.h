/* FILE:	 HC7Segment.h
   DATE:    28/02/13
   VERSION: 0.1
   AUTHOR:  Andrew Davies


Library header for 7 segment LED displays

You may copy, alter and reuse this code in any way you like, but please leave
reference to HobbyComponents.com in your comments if you redistribute this code.
This software may not be used directly for the purpose of selling products that
directly compete with Hobby Components Ltd's own range of products.

THIS SOFTWARE IS PROVIDED "AS IS". HOBBY COMPONENTS MAKES NO WARRANTIES, WHETHER
EXPRESS, IMPLIED OR STATUTORY, INCLUDING, BUT NOT LIMITED TO, IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE, ACCURACY OR LACK OF NEGLIGENCE.
HOBBY COMPONENTS SHALL NOT, IN ANY CIRCUMSTANCES, BE LIABLE FOR ANY DAMAGES,
INCLUDING, BUT NOT LIMITED TO, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES FOR ANY
REASON WHATSOEVER.
*/


#ifndef HC7Segment_h
#define HC7Segment_h

#include "Arduino.h"


///* Pin order for digit select DIO */
//const byte u8PinOut_Digit[] = {7,15,16,8};
extern const byte u8PinOut_Digit[];
//
///* Pin order for segment DIO */
//const byte u8PinOut_Segment[] = {18,14,5,3,2,17,6,4};
extern const byte u8PinOut_Segment[];


/* Bitmap for digits 0 to 9 and - */
const byte u8Digit_Map[] = {252,96,218,242,102,182,190,224,254,230,2};



class HC7Segment
{
  public:
  HC7Segment(byte Digits, bool DigitSelectState);
  void vDisplay_Number(int u16Value);
  void vDisplay_Number(int Value, byte DecimalPoint);


  private:
  void vWrite_Digit(byte Value, bool IncludeDecimalPoint);
  void vSelect_Digit(byte u8Value);
  void vDeselect_Digits(void);

  byte _Digits;
  bool _DigitSelectState;
};

#endif