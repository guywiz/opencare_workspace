# opencare socio semantic analysis
Tulip python utility classes used to process discussion forum data

## Utility classes

Code in this repository emerged from a hackathon session (Hacking Health Bordeaux Oct 21-23 2016) -- thanks for being indulgent. Soused form the raw ddata, while other pieces of code are meant as scripts to be run from the [Tulip GUI](http://tulip.labri.fr "Tulip - Data Visualization Software / Better Visualization through Research").

* Data_import.py imports data from json files (edgeryders views).
	* The resulting graph -- we call the forum_graph -- connects users to content (posts or comments) they authored; comments point to comments or posts; tags are attached to content.
* Projection.py contains two classes, each used to derive different graphs from the original network built from imported data.
	* AT the mment, the only robust class is the one outputting the tag-tag network.
* LiftUp.py is meant as a script, selecting items in the original forum_graph attached to a bunch of pre-selected tags (in the tag-tag graph).

