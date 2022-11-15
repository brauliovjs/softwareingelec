import ddf.minim.*;
velocimetro v=new velocimetro();
Minim minim;
float vel=0;
boolean a = true;
long inicio, fin;
AudioPlayer audio; // audio parte uno

void setup()
{
  minim=new Minim(this);//crear nueva variable minim
  audio=minim.loadFile("1.mp3");//cargas pista 1
  fullScreen();
  v.setSize(3);
  v.setColor(173,168,31);
  v.setColorText(76,212,234);
  v.setPaso(20);
  v.setMinMax(0,200);
  v.setPosicion(width/2,height/2);
}
void draw()
{
  fill (0);
  rect (0,0,width,height);
  v.show();
  stroke (173,168,31);//borde cirulos
  strokeWeight (10);
  fill (100,0,0);
  ellipse ( width/3 ,height/2, 50,50); //circulo donde esta ubicado el boton 1
  ellipse (2*width/3,height/2, 50,50); //circulo donde esta ubicado el boton 1
  
  if ((dist(2*width/3,height/2, mouseX, mouseY)<25)&&(vel<=200)){
    if(a){
      inicio = millis();
      a = false;
    }
    vel+= 0.2;
    v.valor(vel);
    fin = millis();
    if((fin - inicio) > 10000){
      audio.play();
      }
  } else if (vel>0){
    vel-= 0.2;
    v.valor(vel);
    a = true;
    audio.pause();
    }
  if ((dist(width/3,height/2, mouseX, mouseY)<25)&&(vel>0)){
    vel-= 2;
    v.valor(vel);
    fill(255,0,0);
    ellipse (width/3,height/2, 50,50);
    }
  fill(76,212,234);
  text("Freno",width/3-35,height/2-60);
  text("Acelerador",2*width/3-70,height/2-60);
}
