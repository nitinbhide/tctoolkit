#include<stdio.h>
#include<conio.h>
#include<iostream>
#include<iomanip>
#include<cmath>
#include<stdlib.h>
#include<fstream>
#include<string.h>
#include<windows.h>
using namespace std;
const float nuts=340000000.0;

void features(void);

void createlist(int,int,struct node*&); // passing reference to a pointer
void checklist(int*,int*,int**);
void checklistf(float*,float*,float**P);
int findE(int,int);
int findzero(int,int);
void deleteE(int,int);
void del(void);
void controls(void);
void setnull(void);

struct al_list //adj list
{
int row_pos;
int col_pos;
}*pal;

struct node
{
int row;
int col;
struct node *next;
}*start,*begptr,*degen,*beg;

class BASE
{
protected:
int **al;
int s,d,Ns,Nd;
int *supply,*demand,*Tsupply,*Tdemand;
long int Ts,Td,nTs,nTd;
int *spath,shpl;

public:
void allocate(void);
int checkRow(int,int,int*);
int checkCol(int,int,int*);
int loopfinder(int,int,int,int);
};
void BASE::allocate()
{
int i,j;

Tsupply=new int[Ns];
Tdemand=new int[Nd];

for(i=0;i<Ns;i++)
Tsupply[i]=supply[i];
for(j=0;j<Nd;j++)
Tdemand[j]=demand[j];

al=new int*[Ns];

for(i=0;i<Ns;i++)
{
al[i]=new int[Nd];
for(j=0;j<Nd;j++)
al[i][j]=0;
}
}

int BASE ::checkRow(int row,int RTOP,int *Rstack)
{
int f,flagR=0;
for(f=0;f<=RTOP;f++)
{
if(Rstack[f]==row)
{
flagR=1;
break;
}
}
return flagR;
}

int BASE::checkCol(int col,int CTOP,int *Cstack)
{
int flagC=0,f;
for(f=0;f<=CTOP;f++)
{
if(Cstack[f]==col)
{
flagC=1;
break;
}
}
return flagC;
}

int BASE::loopfinder(int di,int dj,int shp,int mem)
{
int k=0,rpos,tal;
int i,j;
if(shp)
tal=Ns+Nd;//Total allocations in adjency matrix
else
tal=mem+1;

pal=new struct al_list[tal];
for(i=0;i<Ns;i++) // finding and storing positions of allocations in a struct
{
for(j=0;j<Nd;j++)
{
if(al[i][j]>0 || findE(i,j))
{
pal[k].row_pos=i;
pal[k].col_pos=j;
k++;
}
else
{
if((i==di)&&(j==dj))
{
rpos=k;
pal[k].row_pos=i;
pal[k].col_pos=j;
k++;
}
}
}
}

int adj_mat[tal][tal];
for(i=0;i<tal;i++) // creating adjency matrix
{
for(j=0;j<tal;j++)
{
if(i==j)
adj_mat[i][j]=0;
else
{
if((pal[i].row_pos==pal[j].row_pos)||(pal[i].col_pos==pal[j].col_pos))
adj_mat[i][j]=1;
else
adj_mat[i][j]=0;
}
}
}

int Tadj_mat[tal][tal]; //Defining Temporary Adj. Matrix
int P_mat[tal][tal]; //Penalty_Matrix
for(i=0;i<tal;i++) // initializing temperory adjency matrix
{
if(i!=rpos)
{
for(j=0;j<tal;j++)
Tadj_mat[i][j]=adj_mat[i][j];
}
else
{
for(j=0;j<tal;j++)
Tadj_mat[i][j]=0;
}
}

int n,count=0;
for(j=0;j<tal;j++)
{
if(adj_mat[rpos][j]==1)
count++;
}

int shPath[tal][tal][tal];//shortest path locator
int s1,s2,z,w; //shortest path

int b=0,mov;
for(n=0;n<count;n++)
{
for(j=b;j<tal;j++) // initializing...
{
if(adj_mat[rpos][j]==1)
{
Tadj_mat[rpos][j]=1;

if(pal[rpos].row_pos==pal[j].row_pos)
{
mov=pal[rpos].row_pos;
for(i=0;i<tal;i++)
{
if(Tadj_mat[j][i]==1)
{
if(pal[i].row_pos==mov)
Tadj_mat[j][i]=0;
}
}
}
else
{
mov=pal[rpos].col_pos;
for(i=0;i<tal;i++)
{
if(Tadj_mat[j][i]==1)
{
if(pal[i].col_pos==mov)
Tadj_mat[j][i]=0;
}
}
}
b=j+1;
break;
}
}

for(i=0;i<tal;i++) // initialising first path matrix
{
for(j=0;j<tal;j++)
{
if(Tadj_mat[i][j]==0)
P_mat[i][j]=30000;
else
P_mat[i][j]=Tadj_mat[i][j];
}
}

if(shp)
{
for(i=0;i<tal;i++) // initializing shortest path matrix with -1
{
for(j=0;j<tal;j++)
{
for(k=0;k<tal;k++)
shPath[i][j][k]=-1;
}
}

for(i=0;i<tal;i++) // initializing shortest path matrix
{
for(j=0;j<tal;j++)
{
if(Tadj_mat[i][j])
{
shPath[i][j][0]=i;
shPath[i][j][1]=j;
}
}
}
}

for(k=0;k<tal;k++) // finding the minimum cost and shortest path matrix
{
for(i=0;i<tal;i++)
{
for(j=0;j<tal;j++)
{
s1=P_mat[i][j];
s2=P_mat[i][k]+P_mat[k][j];
if(s1<s2)
P_mat[i][j]=s1;
else
{
P_mat[i][j]=s2;
if(shp)
{
z=0;
while(shPath[i][k][z]!=-1)
{
shPath[i][j][z]=shPath[i][k][z];
z++;
}
z--;
w=0;
while(shPath[k][j][w]!=-1)
{
shPath[i][j][z+w]=shPath[k][j][w];
w++;
}
}
}
}
}

if(P_mat[rpos][rpos]!=30000)
{
if(shp)
{
shpl=P_mat[rpos][rpos]+1;
spath=new int[shpl];
int a;
for(a=0;a<shpl;a++)
spath[a]=shPath[rpos][rpos][a];
}
return 1;
}
}
}
return 0;
}

class STUDENT : public BASE
{
int **p;
public:
int WAY;
int Mflag;
int counter;

//formating functions
void setsize(int);
void header(int);
void line(int);
void titleBar(int);
void sourceBar(void);
void demandBar(void);
int ways(void);
int methods(void);
int fmethods(void);
void setspace(int,int);

void inputSD(void);
int  getSD(void);
void input(void);  //input functions
int converter(int,int);
bool balancer(void);

void DispTP(int**,int*,int*,long int,long int,int);//output functions
void cost(void);

void VDispTP(int**,int*,int*,long int,long int,int,int,int*,int*,int*,int*);
void ODispTP(int**,int*,int*,long int,long int,int,int*,int*);

//BFS functions
void VAM(void);

int MODI(void);
void check_degenracy(int);
int end(void);
};

void STUDENT ::inputSD()
{
system("mode 33,12");
cout<<"=================================";
cout<<"  TRANSPORTATION COST OPTIMIZER\n";
cout<<"=================================";
cout<<"\n Enter the following details\n";
cout<<"\n Number of Sources(1-9): ";
s=getSD();

cout<<"\n\n Number of Destinations(1-9): ";
d=getSD();
cout<<"\n\n Press any key to continue...";
fflush(stdin);
getch();

}
int STUDENT ::getSD()
{
int x;
char ch;
fflush(stdin);
do
{
ch=getch();
if(ch>=49 && ch<=57)
cout<<ch;
else
cout<<"\a";
}while(ch<49 || ch>57);

switch(ch)
{
case 49:x=1;break;
case 50:x=2;break;
case 51:x=3;break;
case 52:x=4;break;
case 53:x=5;break;
case 54:x=6;break;
case 55:x=7;break;
case 56:x=8;break;
case 57:x=9;break;
}
return x;
}
void STUDENT::setsize(int x)
{
//n=(d*13)+23;+7
switch(x)
{
case 1:system("mode 52,30");break;//exception min size
case 2:system("mode 56,30");break;
case 3:system("mode 69,30");break;
case 4:system("mode 82,30");break;
case 5:system("mode 95,30");break;
case 6:system("mode 108,30");break;
case 7:system("mode 121,30");break;
case 8:system("mode 134,30");break;
case 9:system("mode 147,30");break;
case 10:system("mode 160,30");break;

}
}
void STUDENT ::header(int x)
{
int n,t;
n=(x*13)+23;
cout<<" ";
for(t=1;t<=n;t++)
cout<<"=";
cout<<endl;
}
void STUDENT ::line(int x)
{
int n,k;
n=(x*13)+23;
cout<<" ";
for(k=1;k<=n;k++)
cout<<"-";
cout<<endl;
}
void STUDENT ::titleBar(int x)
{
int t;
cout<<" ";
cout<<setw(6)<<"S\\D";
for(t=1;t<=x;t++)
cout<<setw(12)<<"D"<<t;
cout<<setw(17)<<"Supply"<<endl;

}
inline void STUDENT ::sourceBar(void)
{
cout<<" "<<setw(5)<<"S";
}
inline void STUDENT ::demandBar(void)
{
cout<<" Demand";
cout<<"        ";
}
void STUDENT::setspace(int x,int z)
{
int y,i;
y=(((x*13)+28)/2)-z;
for(i=0;i<y;i++)
cout<<" ";
}

void STUDENT ::DispTP(int **pt,int *sup,int *dem,long int Tsup,long int Tdem,int showE)
{
header(Nd);
titleBar(Nd);
header(Nd);

int i,j;
int flag;
for(i=0;i<Ns;i++)
{
if(i<9)
sourceBar();
else
cout<<" "<<setw(4)<<"S";

cout<<i+1;
cout<<"        ";

for(j=0;j<Nd;j++)
{
flag=1;
if(showE)
{
if(findE(i,j))
{
cout<<setw(5)<<"E";
flag=0;
}
}
if(flag)
{
if(pt[i][j]!=-1)
cout<<setw(5)<<pt[i][j];
else
cout<<setw(5)<<"-";
}

cout<<"        ";
}

cout<<setw(8)<<sup[i]<<endl;


if(i!=Ns-1)
line(Nd);
}

header(Nd);
demandBar();

for(j=0;j<Nd;j++)
{
cout<<setw(5)<<dem[j];
cout<<"        ";
}

cout<<setw(5)<<Tdem<<"\\"<<Tsup<<endl;
header(Nd);
}
void STUDENT ::VDispTP(int **pt,int *sup,int *dem,long int Tsup,long int Tdem,int RTOP,int CTOP,int *Rstack,int *Cstack,int *Rpen,int *Cpen)
{
header(Nd);
titleBar(Nd);
header(Nd);

int i,j;
int flagR,flagC;
for(i=0;i<Ns;i++)
{
if(i<9)
sourceBar();
else
cout<<" "<<setw(4)<<"S";

cout<<i+1;
cout<<"        ";

for(j=0;j<Nd;j++)
{
if(pt[i][j]!=-1)
cout<<setw(5)<<pt[i][j];
else
cout<<setw(5)<<"-";

cout<<"        ";
}

cout<<setw(8)<<sup[i];

flagR=checkRow(i,RTOP,Rstack);
if(flagR!=1)
cout<<setw(4)<<Rpen[i]<<endl;
else
cout<<setw(4)<<"-"<<endl;



if(i!=Ns-1)
line(Nd);
}

header(Nd);
demandBar();

for(j=0;j<Nd;j++)
{
cout<<setw(5)<<dem[j];
cout<<"        ";
}

cout<<setw(5)<<Tdem<<"\\"<<Tsup<<endl;
header(Nd);

cout<<"               ";
for(j=0;j<Nd;j++)
{
flagC=checkCol(j,CTOP,Cstack);
if(flagC!=1)
{
cout<<setw(5)<<Cpen[j];
cout<<"        ";
}
else
{
cout<<setw(5)<<"-";
cout<<"        ";
}
}

cout<<endl;
}
void STUDENT ::ODispTP(int **pt,int *sup,int *dem,long int Tsup,long int Tdem,int showE,int *u,int*v)
{
int i,j;

cout<<" U\\V              ";
for(i=0;i<Nd;i++)
{
cout<<setw(5)<<v[i]<<"        ";
}
cout<<endl;

cout<<"    ";
header(Nd);
cout<<"    ";
titleBar(Nd);
cout<<"    ";
header(Nd);


int flag;
for(i=0;i<Ns;i++)
{
if(i<9)
{
cout<<setw(3)<<u[i]<<" ";
sourceBar();
}
else
{
cout<<setw(3)<<u[i]<<" ";
cout<<" "<<setw(4)<<"S";
}
cout<<i+1;
cout<<"       ";

for(j=0;j<Nd;j++)
{
flag=1;
if(showE)
{
if(findE(i,j))
{
cout<<setw(5)<<"E";
flag=0;
}
}
if(flag)
{
if(pt[i][j]!=-1)
cout<<setw(5)<<pt[i][j];
else
cout<<setw(5)<<"-";
}

cout<<"        ";
}

cout<<setw(8)<<sup[i]<<endl;


if(i!=Ns-1)
{
cout<<"    ";
line(Nd);
}
}

cout<<"    ";
header(Nd);
cout<<"    ";
demandBar();
cout<<"\b";
for(j=0;j<Nd;j++)
{
cout<<setw(5)<<dem[j];
cout<<"        ";
}

cout<<setw(5)<<Tdem<<"\\"<<Tsup<<endl;
cout<<"    ";
header(Nd);
}

void STUDENT ::cost(void)
{
int i,j;
double sum=0;
cout<<"\n";
cout<<" Total Cost = ";
for(i=0;i<Ns;i++)
{
for(j=0;j<Nd;j++)
{
if(al[i][j]!=0 && al[i][j]!=-1)
{
sum=sum+p[i][j]*al[i][j];
cout<<al[i][j]<<"x"<<p[i][j]<<"+";
}
}

}

cout<<"\b \b"<<endl;
cout<<setw(14)<<" = "<<sum<<endl;
}
bool STUDENT :: balancer()
{
if(Ts==Td)
{

nTs=Ts;
nTd=Td;
Ns=s;
Nd=d;
cout<<"\n The given transportation problem is balanced\n"<<endl;
cout<<" Press any key to continue......";
getch();
return true;

}
else
{
cout<<"\n The given transpotation problem is unbalanced"<<endl;
cout<<"\n Press any key to continue......";
getch();
return false;
}
}

void STUDENT :: input()
{
p=new int* [s];
int t;
for(t=0;t<s;t++)
{
p[t]=new int[d];
}

supply=new int[s];
demand=new int[d];

//int n;
setsize(d);
cout<<" ENTER COSTS \n\n";
header(d);
titleBar(d);
header(d);

int j,num;
Ts=Td=0;
for(t=0;t<s;t++)
{

sourceBar();cout<<t+1;
cout<<"           ";

for(j=0;j<d;j++)
{
num=converter(1,1);//if num=-1 then p[t][j]should not be evaluated
p[t][j]=num;
}

num=converter(0,0);
supply[t]=num;
Ts=Ts+num;
cout<<endl;

if(t!=s-1)
{
line(d);
}
}


header(d);

cout<<" Demand";
cout<<"           ";//demand bar

for(j=0;j<d;j++)
{
num=converter(0,1);//if num=-1 then p[t][j]should not be evaluated
demand[j]=num;
Td=Td+num;
}


cout<<Td<<"\\"<<Ts<<endl;

header(d);

}
int STUDENT :: converter(int signal,int adjust)
{
int stack[6];
int TOP=-1,num,t;
int x,flag=1,count=0;
char c;
fflush(stdin);
c=getch();
if(c=='-') //when trasportation not possible b/w Si and Di
{
if(signal)
{
cout<<"-";
cout<<"            ";
Mflag=1;
return -1;
}

}



while(count<5 && (c!=32 || TOP<0))
{
flag=1;
switch(c)
{
case '0':x=0;cout<<x;count++;break;
case '1':x=1;cout<<x;count++;break;
case '2':x=2;cout<<x;count++;break;
case '3':x=3;cout<<x;count++;break;
case '4':x=4;cout<<x;count++;break;
case '5':x=5;cout<<x;count++;break;
case '6':x=6;cout<<x;count++;break;
case '7':x=7;cout<<x;count++;break;
case '8':x=8;cout<<x;count++;break;
case '9':x=9;cout<<x;count++;break;
case '-':if(TOP==-1 && signal==1)
{
cout<<"-";
cout<<"            ";
Mflag=1;
return -1;
}
else
{
cout<<"\a";
flag=0;
}
break;
case  8 :flag=2;break;//backspace
default :cout<<"\a";flag=0;
}

if(flag==1)
{
TOP++;
stack[TOP]=x;
stack[TOP+1]='\0';
}
else if(flag==2 && TOP>-1)
{
cout<<"\b \b";
stack[TOP]='\0';
TOP--;
}

c=getch();
}

num=0;
t=0;
for(x=TOP;x>=0;x--)
{
num=num+stack[x]*pow(10,t);
t++;
}

for(t=1;t<13-TOP && adjust;t++)
cout<<" ";

return num;

}

void STUDENT::VAM(void)
{
allocate();
int Cpen[Nd],Rpen[Ns];
int i,j;
int min1,min2;
int k;
int MaxRpen,MaxCpen;
int r,c;
int min,max;
int diff;
long int TTd=nTd,TTs=nTs;
int Rstack[Ns],Cstack[Nd];
int CTOP=-1,RTOP=-1;
int flagR,flagC;
int sum=0;
int steps=0;
int flag;

do
{

for(i=0;i<Ns;i++) //calculates source penalties
{ min1=min2=32767;
flagR=checkRow(i,RTOP,Rstack);
if(flagR!=1)
{
for(j=0;j<Nd;j++)
{
flagC=checkCol(j,CTOP,Cstack);
if(flagC!=1 && p[i][j]<min1)
{
if(p[i][j]!=-1)
{
min1=p[i][j];
k=j;
}
else
{
al[i][j]=-1;
}
}
}

for(j=0;j<Nd;j++)
{
if(j!=k)
{
flagC=checkCol(j,CTOP,Cstack);
if(flagC!=1 && p[i][j]<min2)
{
if(p[i][j]!=-1)
min2=p[i][j];
}
}
}

if(min2!=32767)
Rpen[i]=min2-min1;
else
Rpen[i]=0;
}

}



for(j=0;j<Nd;j++)//calculates destination penalties
{
min1=min2=32767;
flagC=checkCol(j,CTOP,Cstack);
if(flagC!=1)
{
for(i=0;i<Ns;i++)
{
flagR=checkRow(i,RTOP,Rstack);

if(flagR!=1 && p[i][j]<min1)
{
if(p[i][j]!=-1)
{
min1=p[i][j];
k=i;
}
else
{
al[i][j]=-1;
}
}
}

for(i=0;i<Ns;i++)
{ if(i!=k)
{
flagR=checkRow(i,RTOP,Rstack);
if(flagR!=1 && p[i][j]<min2)
{
if(p[i][j]!=-1)
min2=p[i][j];
}
}
}

if(min2!=32767)
Cpen[j]=min2-min1;
else
Cpen[j]=0;
}
}

MaxRpen=-1;MaxCpen=-1;

for(i=0;i<Ns;i++) //calculates Max of Row penalties
{
flagR=checkRow(i,RTOP,Rstack);

if(flagR!=1)
{
if(Rpen[i]>MaxRpen)
{
MaxRpen=Rpen[i];
r=i;
}
}
}

for(j=0;j<Nd;j++) //calculates Max of Col Penalties
{
flagC=checkCol(j,CTOP,Cstack);
if(flagC!=1)
{
if(Cpen[j]>MaxCpen)
{
MaxCpen=Cpen[j];
c=j;
}
}

}

min=32767;

if(MaxRpen>=MaxCpen)
{
max=MaxRpen;
for(j=0;j<Nd;j++)
{
flagC=checkCol(j,CTOP,Cstack);
if(flagC!=1 && p[r][j]<min)
{
if(p[r][j]!=-1)
{
min=p[r][j];
c=j;
}
}
}
}

else
{
max=MaxCpen;
for(i=0;i<Ns;i++)
{
flagR=checkRow(i,RTOP,Rstack);
if(flagR!=1 && p[i][c]<min)
{
if(p[i][c]!=-1)
{
min=p[i][c];
r=i;
}
}
}
}

steps++;
if(WAY==1)
{
setsize(Nd);
cout<<endl;
setspace(Nd,4);
cout<<"STEP "<<steps<<".1"<<endl<<endl;
}
diff=Tdemand[c]-Tsupply[r];

if(diff<0)
{
al[r][c]=Tdemand[c];
sum=sum+al[r][c];
if(WAY==1)
{
cout<<" COST MATRIX :\n";
VDispTP(p,Tsupply,Tdemand,TTs,TTd,RTOP,CTOP,Rstack,Cstack,Rpen,Cpen);
flag=1;
}
TTd=TTd-Tdemand[c];
TTs=TTs-Tdemand[c];
Tsupply[r]=-diff;
Tdemand[c]=0;
CTOP++;
Cstack[CTOP]=c;
}

else if(diff>0)
{
al[r][c]=Tsupply[r];
sum=sum+al[r][c];

if(WAY==1)
{
cout<<" COST MATRIX :\n";
VDispTP(p,Tsupply,Tdemand,TTs,TTd,RTOP,CTOP,Rstack,Cstack,Rpen,Cpen);
flag=2;
}
TTd=TTd-Tsupply[r];
TTs=TTs-Tsupply[r];
Tdemand[c]=diff;
Tsupply[r]=0;

RTOP++;
Rstack[RTOP]=r;

}

else
{
al[r][c]=Tsupply[r];//or al[r][c]=Tdemand[c]
sum=sum+al[r][c];

if(WAY==1)
{
cout<<" COST MATRIX :\n";
VDispTP(p,Tsupply,Tdemand,TTs,TTd,RTOP,CTOP,Rstack,Cstack,Rpen,Cpen);
flag=3;
}
TTd=TTd-Tdemand[c];
TTs=TTs-Tsupply[r];
Tsupply[r]=Tdemand[c]=0;

RTOP++;
CTOP++;
Rstack[RTOP]=r;
Cstack[CTOP]=c;
}

if(WAY==1)
{
cout<<"\n\n";
cout<<" a)Calculate Penalties"<<endl;
cout<<" b)Identify row/col with max. penalty i.e "<<max<<endl;
cout<<" c)Allocate at min cost i.e at ("<<r+1<<","<<c+1<<")"<<endl;
switch(flag)
{
case 1:cout<<" d)cancel D"<<c+1<<endl;break;
case 2:cout<<" d)cancel S"<<r+1<<endl;break;
case 3:cout<<" d)cancel D"<<c+1<<" and "<<"S"<<r+1<<endl;break;
}

cout<<"\n\n Press Any Key to Continue......";
getch();

setsize(Nd);
cout<<endl;
setspace(Nd,4);
cout<<"STEP "<<steps<<".2"<<endl<<endl;
cout<<" ALLOCATION MATRIX :\n";
DispTP(al,Tsupply,Tdemand,TTs,TTd,0);

cout<<"\n\n Press any key to continue......";
getch();
cout<<endl;
}
}while(sum!=nTs);

if(WAY!=3)
{
setsize(Nd);
cout<<endl;
setspace(Nd,8);
cout<<"FEASIBLE SOLUTION\n\n";
DispTP(al,supply,demand,nTs,nTd,0);
cout<<"\n No. of allocations = "<<steps<<endl;
cost();
if(WAY!=1)
{
cout<<"\n\n Press any key to continue......";
getch();
}
if(WAY==4)
{
exit(0);
}
}
check_degenracy(steps);
}

int STUDENT::MODI(void)
{

int u[Ns],v[Nd];
int i,j,di,dj;
int cpu,min; //cost per unit increment or decrement // d(ij)
int flag=0;

u[0]=0;

for(i=1;i<Ns;i++)
{
u[i]=-32768;
}
for(j=0;j<Nd;j++)
{
v[j]=-32768;
}

for(i=0;i<Ns;i++)
{
for(j=0;j<Nd;j++)
{
if((al[i][j]>0)||(findE(i,j)))
{
if(u[i]!=-32768)
v[j]=p[i][j]-u[i];
else if(v[j]!=-32768)
u[i]=p[i][j]-v[j];
else
createlist(i,j,start);
}
}
}
checklist(u,v,p); // for non degenerate solutions

if(WAY==1)
{setsize(Nd);
cout<<endl;
setspace(Nd,7);
cout<<"OPTIMALITY TEST\n\n";
ODispTP(al,supply,demand,nTs,nTd,1,u,v);

cout<<endl<<"  1)Calculate u's and v's"<<endl;
cout<<"  2)d(i,j)=Cost(i,j)-[u(i,j)+v(i,j)]"<<endl;
cout<<"  3)Find the min of all d(i,j)"<<endl;
}

min=1;//any +ve value will do the job
for(i=0;i<Ns;i++)
{
for(j=0;j<Nd;j++)
{

if(al[i][j]==0 && !(findE(i,j)))
{
cpu=p[i][j]-(u[i]+v[j]);
if(cpu<0)
{
flag=1;
if(cpu<min)
{
min=cpu;
di=i;
dj=j;
}
}

else if(cpu==0&&flag==0)
{
if(!(findzero(i,j)))
{
createlist(i,j,begptr);//value 0 gives another similar optimal solution
createlist(i,j,beg);
}
}
}

}
}


if(flag)
{
if(WAY==1)
cout<<"  4)min = "<<"("<<di+1<<","<<dj+1<<")"<<endl;
}
else
{

if(begptr==NULL)
{
if(WAY==1)
{
cout<<"  4)min > 0"<<endl;
cost();
cout<<"\n  The obtained solution is optimal\n";
cout<<"\n  Press any key to continue......";
getch();

}
else
{
setsize(Nd);
cout<<endl;
setspace(Nd,8);
cout<<"OPTIMAL SOLUTION\n\n";
DispTP(al,supply,demand,nTs,nTd,1);
cost();
cout<<"\n  Press any key to continue......";
getch();
}
return flag;
}
else
{
if(WAY==1)
{
cout<<"  4)min = 0"<<endl;
cost();
cout<<"\n  The obtained solution is optimal\n";
}
else
{
setsize(Nd);
cout<<endl;
setspace(Nd,8);
cout<<"OPTIMAL SOLUTION\n\n";
DispTP(al,supply,demand,nTs,nTd,1);
cost();
}
cout<<"\n\n  Press any key to continue......";
getch();
}
}

if(WAY==1)
{
cout<<"  4)Find a loop that starts and ends at "<<"("<<di+1<<","<<dj+1<<")"<<endl;
cout<<"  5)Required loop : ";
}
loopfinder(di,dj,1,0);//last entry doesn't matter here...

int least=32768,m,n,ki;

if(WAY==1)
{
for(i=0;i<shpl;i++)
{
ki=spath[i];
m=pal[ki].row_pos;
n=pal[ki].col_pos;

cout<<"("<<m+1<<","<<n+1<<")";
if(i<shpl-1)
cout<<"->";
else
cout<<endl;
}


cout<<"  6)Mark "<<"("<<di+1<<","<<dj+1<<")"<<" positive and each position on loop alternately +ve and -ve"<<endl;
cout<<"  7)Find out the minimum allocation at the postions marked -ve"<<endl;
cout<<"  8)This allocation is added or subtracted from the allocations at each position on loop"<<endl;

}

for(i=0;i<shpl-1;i++)
{
if(i%2)
{
ki=spath[i];
m=pal[ki].row_pos;
n=pal[ki].col_pos;
if(al[m][n]<least)
{
least=al[m][n];
if(least==0)
{
deleteE(m,n);
}

}

}
}
for(i=0;i<shpl-1;i++)
{
if(least!=0)
{
ki=spath[i];
m=pal[ki].row_pos;
n=pal[ki].col_pos;
if(i%2)
{
al[m][n]=al[m][n]-least;
}
else
{
if((al[m][n]==0)&&findE(m,n))
{
deleteE(m,n);
}
al[m][n]=al[m][n]+least;
}
}

else
{
//ki=spath[0];
//Ei=pal[ki].row_pos;
//Ej=pal[ki].col_pos;

createlist(di,dj,degen);
break;
}

}
if(WAY==1)
{
cout<<"\n  Press any key to continue......";
getch();

setsize(Nd);
cout<<endl;
setspace(Nd,10);
cout<<"NEW ALLOCATION MATRIX\n\n";
DispTP(al,supply,demand,nTs,nTd,1);

cout<<"\n\n Again check for degenracy...";
getch();
cout<<endl;

}

int steps=0;

for(i=0;i<Ns;i++)
{
for(j=0;j<Nd;j++)
{
if(al[i][j]>0 ||findE(i,j))
steps++;
}
}


check_degenracy(steps);
return flag;

}
void STUDENT::check_degenracy(int steps)
{
int n=(Ns+Nd-1)-steps;

if(n)
{
if(WAY==1)
{
cout<<"\n Obtained solution is degenerate\n"<<endl;
cout<<" Press any key to continue.....";
getch();
setsize(Nd);
cout<<endl;
setspace(Nd,9);
cout<<"REMOVING DEGENRACY\n\n";
}
exit(0);

if(WAY==1)
{
DispTP(al,supply,demand,nTs,nTd,1);
cout<<endl<<endl;
cout<<" a)Level of degenracy = "<<n<<endl<<endl;
cout<<" b)No. of E's to be used = "<<n<<endl<<endl;
cout<<" c)Put E in empty cells such that\n";
cout<<"   it doesn't form a loop\n";
cout<<"\n Press any key to continue.....";
getch();
}
}
else
{
if(WAY==1)
{
cout<<"\n Obtained solution is BFS and non degenerate\n"<<endl;
cout<<" Press any key to continue.....";
getch();
}
}
}

int STUDENT::end()
{
int x;
char ch;
system("mode 41,16");
cout<<"=========================================";
cout<<"      TRANSPORTATION COST OPTIMIZER\n";
cout<<"=========================================";
cout<<endl;
cout<<" 1.Solve a new transportation problem\n";
cout<<"-----------------------------------------";
cout<<" 2.Exit\n";
cout<<"-----------------------------------------";
cout<<" Enter choice(1-2): ";
fflush(stdin);
while(1)
{
ch=getch();
if(ch>48 && ch<52)
{
cout<<ch;
switch(ch)
{
case 49:x=1;break;
case 50:x=2;break;
}
cout<<"\n\n";
cout<<" Press any key to continue...";
getch();
return x;
}
else
cout<<"\a";
}
}

int main()
{
int en;
controls();
STUDENT A;
choice2:
A.Mflag=0;
int m;
A.inputSD(); //Supply Demand I/p Screen
A.input(); // Problem Input
bool bal = A.balancer(); //CHECK IF BALANCED OR NOT
if(bal==false)
goto anth;
A.VAM();
system("mode 41,17");
while(A.MODI());
anth:
en=A.end();
if(en==1)
goto choice2;
else
exit(0);
return 0;
}

void controls()
{
system("mode 45,15");
cout<<"=============================================";
cout<<"        TRANSPORTATION COST OPTIMIZER\n";
cout<<"=============================================";
cout<<endl;
cout<<"                  CONTROLS\n";
cout<<"---------------------------------------------";
cout<<" 1.Transportation not possible  -> -\n";
cout<<"---------------------------------------------";
cout<<" 2.Jump to next row             -> Space Bar\n";
cout<<"---------------------------------------------";
cout<<" 3.Jump to next column          -> Space Bar\n";
cout<<"---------------------------------------------";
cout<<"\n Press any key to continue.......";
fflush(stdin);
getch();

}
void createlist(int r,int c,struct node* &star)
{
if(star==NULL)
{
star=new struct node;
star->row=r;
star->col=c;
star->next=NULL;
return;
}

else
{ struct node *x,*y;

x=star;
while(x->next!=NULL)
{
x=x->next;
}

y=new struct node;
y->row=r;
y->col=c;
y->next=NULL;
x->next=y;
}

}
void checklist(int *U,int *V,int **P)
{
struct node *x,*y,*temp;
int r,c;

if(start==NULL)
{
return;
}

else
{ while(start!=NULL)
{
x=start;
y=x;
while(x!=NULL)
{
r=x->row;
c=x->col;

if(U[r]!=-32768)
{
V[c]=P[r][c]-U[r];
break;
}
else if(V[c]!=-32768)
{
U[r]=P[r][c]-V[c];
break;
}
else
{
y=x;
x=x->next;
}
}

if(x==start)
{
start=x->next;
temp=x;
delete temp;
}

else
{
y->next=x->next;
temp=x;
delete temp;
}

}
}

}
int findE(int r,int c)
{
struct node *x;
if(degen==NULL)
{
return 0;
}
else
{
x=degen;
while(x!=NULL)
{
if(x->row==r && x->col==c)
{
return 1;
}
x=x->next;
}

return 0;
}
}
int findzero(int r,int c)
{
struct node *x;
if(beg==NULL)
{
return 0;
}
else
{
x=beg;
while(x!=NULL)
{
if(x->row==r && x->col==c)
{
return 1;
}
x=x->next;
}

return 0;
}
}
void deleteE(int r,int c)
{
struct node *temp;

if(degen->row==r && degen->col==c)
{

temp=degen;
delete temp;
degen=NULL;
}

else
{
struct node *x,*y;
x=degen;
y=x;
x=x->next;
while(x!=NULL)
{
if(x->row==r && x->col==c)
{
y->next=x->next;
temp=x;
delete temp;
break;
}

y=x;
x=x->next;
}

}


}
void del(void)
{
struct node *temp;
temp=begptr;
begptr=begptr->next;
delete temp;

}
void checklistf(float *U,float *V,float **Pf)
{
struct node *x,*y,*temp;
int r,c;

if(start==NULL)
{
return;
}

else
{ while(start!=NULL)
{
x=start;
y=x;
while(x!=NULL)
{
r=x->row;
c=x->col;

if(U[r]!=-nuts)
{
V[c]=Pf[r][c]-U[r];
break;
}
else if(V[c]!=-nuts)
{
U[r]=Pf[r][c]-V[c];
break;
}
else
{
y=x;
x=x->next;
}
}

if(x==start)
{
start=x->next;
temp=x;
delete temp;
}

else
{
y->next=x->next;
temp=x;
delete temp;
}
}
}
}
