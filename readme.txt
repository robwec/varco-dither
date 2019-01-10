I wanted to play with image dithering algorithms.

useful pages for learning about image dithering:
https://en.wikipedia.org/wiki/Dither
	overview
http://caca.zoy.org/study/part3.html
	useful tutorial, explanations, and overview
http://www.efg2.com/Lab/Library/ImageProcessing/DHALF.TXT
	another overview
http://caca.zoy.org/attachment/wiki/publications/2008-displacement.pdf
	Sam Hocevar and Gary Niger, "Reinstating Floyd-Steinberg: Improved Metrics for Quality Assessment of Error Diffusion Algorithms"
	particularly the comment about the modified Floyd-Steinberg kernel with only three weights 1/16{7,4,5} instead of four weights 1/16{7,3,5,1}.
http://www2.units.it/ramponi/teaching/DIP/materiale/z04_halftone_ErrorDiffusion.pdf
	Xiangyu Y.Hu's paper, "Simple gradient-based error-diffusion method"
	this method uses a lot of randomization and results look somewhat different than the initial Floyd_Steinberg kernel.
	I tried variations of this method with different kernels and with Ostromoukhov's kernel, where the weights vary by the intensity of the propagating pixel.
http://www.iro.umontreal.ca/~ostrom/varcoeffED/
	Victor Ostromoukhov. A Simple and Efficient Error-Diffusion Algorithm. To appear in Proceedings of SIGGRAPH'01.
https://perso.liris.cnrs.fr/victor.ostromoukhov/publications/publications_abstracts.html
	particularly Stochastic Clustered-Dot Dithering, which proposes an unusual method for filling an image with shapes to approximate the correct intensity.
https://codegolf.stackexchange.com/questions/26554/dither-a-grayscale-image
	a bunch of codes and image outputs. I observe that the artifacts in "noise addition plus basic diffusion" look similar to the gradient-based diffusion that Hu proposed.
http://www.tannerhelland.com/4660/dithering-eleven-algorithms-source-code/
	more overview and examples
	https://news.ycombinator.com/item?id=15413377

ImageMagick has a dithering option that uses Floyd-Steinberg. It's one quick way to run a dither without installing much stuff. Here's what one such command might look like:
	convert "in.png" -background white -alpha remove -resize 384 -density 203 -dither FloydSteinberg -depth 4 -colors 16 -remap pattern:gray50 "out.jpg"
what those things do:
	-background white -alpha remove to remove transparency (it gets converted to black without this)
	-resize 384 -density 203 for printing on a 58mm thermal printer at 203 DPI
	-dither FloydSteinberg calls the dither
	-depth 4 -colors 16 to control the dither, and -remap pattern:gray50 so it converts the dither correctly to monochrome.
There's also ordered dither in ImageMagick, which I would call with
	convert "in.png" -background white -alpha remove -colorspace gray -resize 384 -density 203 -ordered-dither o8x8 "out.jpg"

...

It seems like it might also be possible to run a neural network to dither, provided you can define or obtain an appropriate error function (like "How good does this dithered output image look?, and how close is it to the original?").

I couldn't find much regarding this idea, although I did find a few papers for dithering + neural networks.
	https://arxiv.org/abs/1707.00116
		Image Companding and Inverse Halftoning using Deep Convolutional Neural Networks
		uses a convolutional neural network to try and invert dithering, reproducing the original image. That's interesting.
	https://arxiv.org/abs/1508.04826
		"Dither is Better than Dropout for Regularising Deep Neural Networks'
		1: I'd like to implement this.
		2: I was also thinking that pre-dithering inputs can be, in some cases, a way of reducing the sensitivity of a network to small but insignificant details. Add noise to protect against small, bad signals.

...

final result workflow: preprocess in Python, do dithering in C#, then do some more processing; it's all linked in batchprocess.py. Can tweak the C# code to probably do some more stuff, but whatever. There are also some batch scripts that call the Python edits for individual images dragged and dropped onto the scripts; maybe good for testing some stuff.

...
2018-04-12-1829-59
while working on another image processing thing, I read about Otsu binarization. Apparently, a combination of Otsu binarization plus ordered-dither can produce decent results quickly. It's different than the other stuff I had looked at, so I felt it was worth noting.
	https://www.atlantis-press.com/php/download_paper.php?id=19745
	ftp://ftp.repec.org/opt/ReDIF/RePEc/rau/jisomg/WI12/JISOM-WI12-A18.pdf