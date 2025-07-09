#include <stdio.h>
// #include <cs50.h>
void print_row(int w);

int main(void)
{
    const int n = 6;
    for ( int i = 0; i< n; i++)
    {
        print_row(n);

    }

}
void print_row(int w)
{
for (int i = 0; i <w; i++)
{
    printf("#");
}
printf("\n");
}
