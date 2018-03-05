char input;

void setup()
{
  pinMode(7, OUTPUT);
  pinMode(8, OUTPUT);
  pinMode(13, OUTPUT);
  Serial.begin(1000000);
}

void loop()
{
  if (Serial.available() > 0)
  {
    input = Serial.read();
    if (input == '1')
    {
      digitalWrite(13, LOW);
      digitalWrite(7, HIGH); //Enabling TX
      digitalWrite(8, LOW);  //Disabling RX
      Serial.print(1);
    }
    else
    {
      digitalWrite(13, HIGH);
      digitalWrite(7, LOW);  //Disabling TX
      digitalWrite(8, HIGH); //Enabling RX
      Serial.print(0);
    }
    
  }
  
}
