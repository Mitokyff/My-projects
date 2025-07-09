#include <stdio.h>
#include <cs50.h>
void row(int r);


int main(void)
{
  int h;
  do {
      h = get_int("What's is the height of the pyramid");
  }
  while (h < 1 );
    for (int i= 1; i <= h; i++)
    {
  row (i) ;
}
    } 

void row(int r)
{
    for (int i = 0; i < r; i++)
    {
        printf("#");
    }
    printf("\n");
}
