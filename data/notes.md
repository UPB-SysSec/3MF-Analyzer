# Notes

## Test Ideas/TODO

- Maybe the title of an object is displayed (slic3r does it in an object-selection dropdown). Injection that way?

- check generated output of software for special extensions/metadata (e.g. from STL -> 3MF)
- script that analyses the models outputted (if 3MF export exists)
  - would be nice for infos like: "program xyz cannot load model by abc"

- metadata name tag not restricted in XSD
  - means if XSD used to verify might accept non valid XMLs
- XSD for slice is wrong (some attributes are required, that should not be)

## Metadata Viewable

Metadata is the only way to do XXE Attacks (only place where an XML element has an actual value and not just children/attributes).
List where/which metadata is viewable in a program and if an object's name is displayed.

| Program Name  | Shows Object MD    | Shows BuildItem MD | Shows Model MD                 | Object Name        |
| ------------- | ------------------ | ------------------ | ------------------------------ | ------------------ |
| 3D Builder    | n (shows filename) | n (shows filename) | y (sidebar "About this model") | n                  |
| 3D Viewer     | n                  | n                  | n                              | n                  |
| CraftWare Pro | n (shows filename) | n (shows filename) | n (shows filename)             | n                  |
| Cura          | n (shows filename) | n (shows filename) | n (shows filename)             | n                  |
| FlashPrint    | n                  | n                  | n                              | n                  |
| Fusion 360    | n                  | n                  | n                              | n                  |
| ideaMaker     | n (shows filename) | n (shows filename) | n (shows filename)             | y (distinct parts) |
| lib3mf        | N/A                | N/A                | N/A                            | N/A                |
| Lychee Slicer | n (shows filename) | n (shows filename) | n (shows filename)             | n                  |
| Paint 3D      | n                  | n                  | n                              | n                  |
| PrusaSlicer   | n (shows filename) | n (shows filename) | n (shows filename)             | y (distinct parts) |
| Simplify3D    | n (shows filename) | n (shows filename) | n (shows filename)             | n                  |
| Slic3r        | n (shows filename) | n (shows filename) | n (shows filename)             | y (combined part)  |
| Z-Suite       | n (shows filename) | n (shows filename) | n (shows filename)             | n                  |

## Evaluation

- which extensions are supported (fail vs ignore) (which F-B-* test is "loaded")
- DTDs consequently failed (all XML-* "aborted")
- XML not failed but see no wrong behavior (DTD ignored)
- DoS possible
- content spoofing possible

### Observations

- when slice extension ignored, obv. the cs/dos attacks with it don't work as well
- zsuite seems to load two models for the ZIP tests
- prusa doesn't load for invalid files. can't distinguish crashes and invalid files
- lib3mf doesn't load anything other than mesh when converting to STL
- prusa stores config in 3MF

| Name          |   Materials   | Production |  Slice  | Beam-Lattice |
| :------------ | :-----------: | :--------: | :-----: | :----------: |
| 3D Builder    |    loaded     |   loaded   | ignored |   ignored    |
| 3D Viewer     |    loaded     |  aborted   | aborted |   ignored    |
| Craftware Pro | loaded (mesh) |  aborted   | aborted |   ignored    |
| Cura          | loaded (mesh) |   loaded   | ignored |   aborted    |
| Flashprint    | loaded (mesh) |   loaded   | ignored |   aborted    |
| Fusion 360    | loaded (mesh) |  aborted   | aborted |   aborted    |
| ideaMaker     | loaded (mesh) |   loaded   | ignored |   aborted    |
| lib3mf        | loaded (mesh) |  aborted   | aborted |   ignored    |
| Lychee Slicer | loaded (mesh) |   loaded   | ignored |   aborted    |
| Paint 3D      |    loaded     |   loaded   | ignored |   aborted    |
| PrusaSlicer   | loaded (mesh) |   loaded   | ignored |   aborted    |
| Simplify3D    | loaded (mesh) |   loaded   | aborted |   ignored    |
| Slic3r        | loaded (mesh) |   loaded   | ignored |   ignored    |
| Z-Suite       | loaded (mesh) |   loaded   | aborted |   ignored    |

### DoS

- DOS-BL-MBR works for many programs (some seem to handle it pretty well)
- lychee effectively DoS'ed if a file is invalid. Tries to recover from it, doesn't seem to handle correctly (at least on startup, when imported "loading" indefinitely)
- several crashes in different programs
- ideamaker seems to hang if reference invalid
- slic3r sometimes only crashes if object selected manually

### Content Spoofing

#### Reference Confusion

- reference confusion on unused elements is mostly ignored
  - different behavior between programs, that load an element and those that don't

##### Referenced Object Duplication

- CS-DOID/GEN-C-CDA-RESOURCES-1 often loaded one model, which one varies (sometimes both)
- different models through different materials/colors (even core spec) mostly not possible
  - most programs ignore materials (understandable for slicers)
  - those that don't parse correctly
- 3dbuilder sometimes ignores duplicate property, sometimes not?

##### Referenced Object Broken

- lychee breaks mesh completely if invalid ref? (GEN-C-AI-BASEMATERIALS-ID-0, GEN-C-CR-RESOURCES-BASEMATERIALS-0)
- some programs ignore object with invalid ID/references to not-existing elements

#####  Reference Broken

##### Model Reference Functionality

| Program    | 0000  | 0001  | 0010  | 0011  | 0100  | 0101  | 0110  | 0111  | 1000  | 1001  | 1010  | 1011  | 1100  | 1101  | 1110  | 1111  |
| :--------- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| SHOULD     |       |       |       |   C   |       |       |       |  (C)  |       |       |       |   C   |   P   |  (P)  |   P   |       |
| :--------- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 3dbuilder  |       |       |       |   C   |       |       |       |       |       |       |       |   C   |   P   |       |   P   |   P   |
| 3dviewer   |       |       |       |   C   |       |       |       |       |       |       |       |   C   |   P   |       |   P   |   P   |
| craftware  |       |       |       |   C   |       |       |       |       |       |       |       |   C   |   P   |       |   P   |   P   |
| cura       |       |       |       |       |       |       |       |       |   P   |   P   |   P   |   P   |   P   |   P   |   P   |   P   |
| flashprint |       |       |       |   C   |       |       |       |       |       |       |       |   C   |   P   |       |   P   |       |
| fusion     |       |       |       |   C   |       |       |       |       |       |       |       |   C   |   P   |       |   P   |   P   |
| ideamaker  |       |       |   C   |   C   |       |       |   C   |   C   |   P   |   P   |  CP   |  CP   |   P   |   P   |  CP   |  CP   |
| lib3mf     |       |       |       |   C   |       |       |       |       |       |       |       |   C   |   P   |       |   P   |   P   |
| lychee     |       |       |       |   C   |       |       |       |       |       |       |       |   C   |   P   |   P   |   C   |   C   |
| paint3d    |       |       |       |   C   |       |       |       |       |       |       |       |   C   |   P   |       |   P   |   P   |
| prusa      |       |       |   C   |   C   |       |       |   C   |   C   |   P   |   P   |       |       |   P   |   P   |       |       |
| simplify   |       |       |   C   |   C   |       |       |   C   |   C   |   P   |   P   |   P   |   P   |   P   |   P   |   P   |   P   |
| slic3r     |       |       |       |       |       |       |       |       |   P   |   P   |   P   |   P   |   P   |   P   |   P   |   P   |
| zsuite     |       |       |   C   |   C   |       |       |   C   |   C   |   P   |   P   |  CP   |  CP   |   P   |   P   |  CP   |  CP   |

- 100% correct behavior
  - flashprint
- 99% correct behavior (don't fail in 1111)
  - 3dbuilder
  - 3dviewer
  - craftware
  - fusion
  - lib3mf
  - paint3d
- 90% correct behavior (ignores invalid references)
  - lychee (ignored for 1101, but not 0111)
- load only 3dmodel.model and ignore references
  - cura
  - slic3r
- load every existing 3D model part, regardless of references
  - ideamaker (loads both, if both exists)
  - zsuite (loads both, if both exists)
  - simplify (loads 3dmodel.model, if both exists)
  - prusa (fails, if both exists)

- 1111 (no real behavior specified, but there should only be one 3D model part)
  - most that load one model load the first in the .rels XML (only lychee loads the 2nd)

- for example using 1011 loads model A in seven cases, B in three cases, and both in two cases

#### Property Confusion

- some ignore transformation
- some use first transformation, some second if there are two
  - 1st: cura
  - 2nd: 3dviewer, fusion, lib3mf
  - slic3r multiplies? GEN-M-ADA-ITEM-TRANSFORM-0
- some always use the default millimeter unit others adhere to the attribute (they also fail with a wrong attribute)
- all seem to ignore supports
