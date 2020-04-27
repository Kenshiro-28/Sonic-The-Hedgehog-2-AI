# Sonic The Hedgehog 2 AI

This is a Sonic The Hedgehog 2 artificial intelligence based on the T-Rex evolutionary neural network. It trains playing the game until it's unable to improve its best score. After completing the training, the program plays a last game rendering the game screen.

## Game information

Sonic the Hedgehog 2 is a platform game developed and published by Sega for the Sega Genesis console, released worldwide in November 1992. It is the second main entry in the Sonic the Hedgehog series, and introduced Sonic's sidekick, Miles "Tails" Prower, controllable by a second player. In the story, Sonic and Tails must stop series antagonist Dr. Ivo Robotnik from stealing the Chaos Emeralds to power his space station, the Death Egg.

Development of the game began in November 1991. The game was developed by both Japanese and American staff at Sega Technical Institute. The game was directed by Masaharu Yoshii and produced by Shinobu Toyoda, with game design led by Hirokazu Yasuhara and music composed by Masato Nakamura. Art director Tim Skelly designed the appearance of the new 3D special stages based on a tech demo created by Yuji Naka. The staff increased the speed of Sonic the Hedgehog 2 in comparison to its predecessor.

Sonic the Hedgehog 2 sold over six million copies, making it the second-bestselling Genesis game behind the original Sonic the Hedgehog. Cited as one of the greatest video games of all time, it received acclaim from critics who commended the game's level design, visuals and music.

This program uses the Sega Genesis console emulator provided by OpenAI Gym Retro.

## Neural network information

T-Rex is an evolutionary neural network. It learns by adjusting the strength of the connection weights by mutation and selection. The programmer must define the problem to solve with a scoring system so that T-Rex can evolve gradually until finding the optimal solution.

Main features:

- Binary feedforward neural network
- Configurable number of inputs, hidden layers and outputs
- Developed using object-oriented programming
- Fast, robust and portable

### Input layer

The input of the neural network is the screen output of the Sega Genesis console. The original image is processed with Canny edge detection to extract useful structural information and dramatically reduce the amount of data to be processed. The first 44 lines of the screen are ignored to further reduce the amount of data. Finally, the image resolution is reduced to one sixth of its original size. The input layer has 9600 neurons.

### Hidden layers

The neural network has 2 hidden layers. The T-Rex architecture states that the number of neurons in each hidden layer is set as the number of input neurons so they have 9600 neurons.

### Output layer

The neural network outputs are the button activations on the player's gamepad. As the game emulation provides 12 buttons, the output layer has 12 neurons.

## Installing dependencies

### T-Rex

You must compile T-Rex as a shared library:

https://github.com/Kenshiro-28/T-Rex

Copy the generated file **libT-Rex.so** in the folder /usr/local/lib

### Python

Run this command to install Python:

```
$ sudo apt install python3-dev python3-pip python3-wheel python3-opencv
```

### OpenAI Gym Retro

Run this command to install OpenAI Gym Retro:

```
$ pip3 install gym-retro
```

### Game ROM

This program has been tested with the world version of the game. Run this command in the folder containing the ROM file:

```
$ python3 -m retro.import ./
```

## Running

Run this command in the root folder to start the program:

```
$ python3 sonic2.py
```

This project includes a trained neural network. Running the program will skip the training phase if there is a neural network file in the same folder. To train a new neural network, delete the file **neural_network.json**.

----- Work in progress -----
