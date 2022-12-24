Table table;
String[] labels;
int[][] colors;

void setup() {

  table = loadTable("/Users/lucasgover/spotify_python/spotify_wrapped.csv", "header");

  String x = table.getColumnTitle(0);
  labels = new String[table.getColumnCount()-1];
  for(int i = 0; i < labels.length; i++){
    labels[i] = table.getColumnTitle(i+1);
    println(labels[i]);
  }
  size(1200,600);
  colors = new int[table.getColumnCount()-1][];
  for(int i = 0; i < colors.length; i++){
    colors[i] = new int[3];
  }
  colors[0][0] = 100; colors[0][1] = 225; colors[0][2] = 100; //0
  colors[1][0] = 255; colors[1][1] = 50; colors[1][2] = 50; // 1
  colors[2][0] = 50; colors[2][1] = 215; colors[2][2] = 215; // 2
  colors[3][0] = 255; colors[3][1] = 175; colors[3][2] = 50; // 3
  colors[4][0] = 185; colors[4][1] = 100; colors[4][2] = 230; // 4
}

void draw(){
  background(255);
  noStroke();
  for(int i =4; i >=0;i--){
    fill(colors[i][0],colors[i][1],colors[i][2]);
    beginShape();
    vertex(100,60);
    for(int j = 0; j < table.getRowCount(); j++){
      vertex(100+(j * (width-200))/table.getRowCount(),60+(height-120)*weightedAverage(i,j));
    }
    vertex((width-100),60);
    endShape();
    fill(colors[i][0],colors[i][1],colors[i][2]);
  }
}

float weightedAverage(int column,int row){
  float sum = 0;
  float total=0;
  for(int i = max(0,row-20); i < min(row+20,table.getRowCount()); i++){
    float dist = abs(i-row)+1;
    float weight = 1.0/(dist);
    //weight = 0.5+(0.5*weight);
    println(weight);
    sum += (float(table.getString(i,column+1)) * weight);
    total += weight;
  }
  return sum/total;
}
