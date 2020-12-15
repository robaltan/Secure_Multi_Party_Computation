# Ben-Or, Goldwasser and Wigderson (BGW) Protocol 
The main goal of using a multi-party protocol is to make sure that shared calculations could be carried out to get an output while making sure that every party’s inputs remain private. A classical example that motivates the implemen- tation of multi-party computation is the millionaire’s problem, where multiple parties would aspire to learn who is the wealthiest among themselves without revealing their wealth to one another. 

## Testing

To see whether the results of the BGW protocol is correct, it's enough to run the MakeFile. Run the following command in the terminal in the directory where this project is located:

```shell
make
```