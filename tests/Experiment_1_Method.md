# Experiment 1:

Our machine learning integration of BETSE will be tested using an experimental setup defined by Pietak & Levin, 2018, wherein they defined a simple cell group of size 7 and applied five different global interventions to the group over 12 minutes in BETSE. The parameters for the simulation are defined using the physiology\_2018.yaml config file [downloadable along with other data related to the experiment here.](https://www.dropbox.com/scl/fi/t45ukr912u3a5fumgogf9/Physiology.zip?rlkey=ryvbq5nts61nsoqb1b2ma9dow&e=1&dl=0) 

To start, we define a list of parameters within this configuration file to optimize that 1\) can cause changes in Vmem and 2\) can reasonably be modulated in vivo. Special thanks to Hazan, 2022 for their work done in defining many of these parameters. Each parameter is accompanied by a “/”-delimited path, similar to a file path, which is used to locate parameters and either insert or extract them from the nested objects in the .YAML file. This approach to .YAML file manipulation was done from scratch, so better architecture may be available out there. [Click for more .YAML documentation.](https://pyyaml.org/wiki/PyYAMLDocumentation) 17 parameters were selected for this test:

PARAMETER LIST

| Parameter | YAML “path” |
| :---- | :---- |
| Cl\- Diffusion Rate | config/tissue profile definition/tissue/default/diffusion constants/Dm\_Cl |
| Na\+ Diffusion Rate | config/tissue profile definition/tissue/default/diffusion constants/Dm\_Na |
| K\+ Diffusion Rate | config/tissue profile definition/tissue/default/diffusion constants/Dm\_K |
| Ca\+ Diffusion Rate | config/tissue profile definition/tissue/default/diffusion constants/Dm\_Ca |
| Gap Junction Surface Area | config/variable settings/gap junctions/gap junction surface area |
| Gap Junction Minimum | config/variable settings/gap junctions/gj minimum |
| Gap Junction Voltage Threshold | config/variable settings/gap junctions/gj voltage threshold |
| Change rate of K\+ intervention | config/change K env/change rate |
| K\+ intervention concentration multiplier | config/change K env/multiplier |
| Ouabain intervention change rate | config/general network/biomolecules/change at bounds/change rate\_Ouabain |
| cAMP intervention change rate | config/general network/biomolecules/change at bounds/change rate\_cAMP |
| X intervention change rate | config/general network/biomolecules/change at bounds/change rate\_X |
| Y intervention change rate | config/general network/biomolecules/change at bounds/change rate\_Y |
| Ouabain maximum concentration | config/general network/biomolecules/change at bounds/concentration\_Ouabain |
| cAMP maximum concentration | config/general network/biomolecules/change at bounds/concentration\_cAMP |
| X maximum concentration | config/general network/biomolecules/change at bounds/concentration\_X |
| Y maximum concentration | config/general network/biomolecules/change at bounds/concentration\_Y |

### Explanation of YAML path strings

The path string begins with a root:

**config**/general network/biomolecules/change at bounds/concentration/_Y

 which at this point can only be defined to be “config” or “grn”. If the root is config, then it simply traverses the .YAML file passed into the python parameter insertion function. If the root is “grn”, the function will instead open the config file at the path listed under “gene regulatory network settings/gene regulatory network config” and traverse the path from there. 

The body of the path defines the sequence of nested objects that must be accessed to arrive at the location of the desired parameter in the config file:

config/**general network/biomolecules/change at bounds/concentration/**_Y

Finally, parameters optionally have an underscore at the end of the path:

config/general network/biomolecules/change at bounds/concentration/***_Y***

The string after the underscore is a name, used for identifying the parameter among duplicate parameters typical of a list of chemical definitions in BETSE config files. Specifically, the “biomolecules” section in the config file is not an object, but a YAML list of molecules with specific attributes. Each object in the list has a “name” field, and the string after the underscore is matched with the “name” in order to proceed with the search.

Using the above example as input, the parameter insertion function will do the following:

1. Read the root and open the YAML configuration file passed in to the top level function  
2. Open the “general network section”, and search within for the “biomolecules” section.  
3. Open the “biomolecules” section, and detect that “biomolecules” is a list.  
4. Traverse the list of biomolecules for one with a “name” field containing “Y”.  
5. Open the object with the name “Y” and search within for the “change at bounds” section.  
6. Search in the “change in bounds” section for “concentration”.  
7. Change the value of “concentration.  
8. Done\! Repeat for the next parameter.

### Interventions

For this first test, the full simulation is designed to run over a period of sixty seconds. The following interventions are scheduled in the simulation (Taken from Pietak’s documentation *BETSE Tutorials):*

- *5-10 seconds*, drug 'X' is added to the environment and blocks a K+ leak channel, cells depolarize  
- *15-20* seconds, drug 'Y', a Na+ channel agonist, is added to the environment, cells depolarize  
- *25-30* seconds, the Na/K-ATPase pump is blocked by addition of ouabain, cells depolarize slightly  
- *35-40* seconds, cAMP is added to the environment, which activates an H,K-ATPase pump, cell pH increases  
- *45-50* seconds, a potassium salt, K+/M- is added to the environment, cells depolarize

At the end of each event, the environmental concentration of the target substance returns to normal, and there is a cooldown period in which we can observe how the cell reacts. The parameters that the RL architecture has to play with are the rates of change of a substance concentration in the environment during the test, and the peak concentration during the event. All of these concentrations are measured in mmol/L, with the notable exception of K\+, which measures concentration as a multiplier of the concentration found in the environment at the beginning of the intervention. 

