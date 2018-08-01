/* FILE:	 HC7Segment.cpp
   DATE:    28/02/13
   VERSION: 0.1
   AUTHOR:  Andrew Davies

Library for 7 segment LED displays

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



#include "Arduino.h"
#include "HC7Segment.h"


/* Constructor to initiliase the GPIO as outputs and in the OFF state*/
HC7Segment::HC7Segment(byte Digits, bool DigitSelectState)
{

  byte LED_Cur_Digit;
  byte LED_Cur_Segment;
  _Digits = Digits;
  _DigitSelectState = DigitSelectState;



  for (LED_Cur_Digit = 0; LED_Cur_Digit < _Digits; LED_Cur_Digit++)
  {
    pinMode (u8PinOut_Digit[LED_Cur_Digit], OUTPUT);
    digitalWrite(u8PinOut_Digit[LED_Cur_Digit], !_DigitSelectState);
  }

  for (LED_Cur_Segment = 0; LED_Cur_Segment < 8; LED_Cur_Segment++)
  {
    pinMode (u8PinOut_Segment[LED_Cur_Segment], OUTPUT);
    digitalWrite(u8PinOut_Segment[LED_Cur_Segment], _DigitSelectState);
  }

}



void HC7Segment::vDisplay_Number(int Value)
{
  byte Loop;
  bool IsNegative = Value < 0;


  for (Loop = 0; Loop < _Digits; Loop++)
  {
    vDeselect_Digits();

    if (Loop == (_Digits - 1) && IsNegative)
	{
		vWrite_Digit(10, 0);
	}else
	{
   		vWrite_Digit(abs(Value) % 10, 0);
	}

    Value /= 10;
    vSelect_Digit(Loop);
  }

  vDeselect_Digits();
}

void HC7Segment::vDisplay_Number(int Value, byte DecimalPoint)
{
  byte Loop;
  bool IsNegative = Value < 0;

  for (Loop = 0; Loop < _Digits; Loop++)
  {
    vDeselect_Digits();

    if (Loop == (_Digits - 1) && IsNegative)
    {
		vWrite_Digit(10, 0);
	}else
	{
    	vWrite_Digit(abs(Value) % 10, Loop + 1 == DecimalPoint);
	}
    Value /= 10;
    vSelect_Digit(Loop);
  }
  vDeselect_Digits();
}



void HC7Segment::vWrite_Digit(byte Value, bool IncludeDecimalPoint)
{
  byte Loop;

  for(Loop = 0; Loop < 8; Loop++)
  {
   digitalWrite(u8PinOut_Segment[Loop], (~((u8Digit_Map[Value] >> 7-Loop) ^ !_DigitSelectState))&1);
  }

  if(IncludeDecimalPoint)
  	digitalWrite(u8PinOut_Segment[7], !_DigitSelectState);
}



void HC7Segment::vSelect_Digit(byte Value)
{
  byte Loop;

  for (Loop = 0; Loop < _Digits; Loop++)
  {
    digitalWrite(u8PinOut_Digit[Loop],!_DigitSelectState);
  }

  digitalWrite(u8PinOut_Digit[Value],_DigitSelectState);
}



void HC7Segment::vDeselect_Digits(void)
{
  byte Loop;

  for (Loop = 0; Loop < _Digits; Loop++)
  {
  	digitalWrite(u8PinOut_Digit[Loop],!_DigitSelectState);
  }
}