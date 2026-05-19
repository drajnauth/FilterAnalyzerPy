# Filter Analyzer
This is an update the the Java filter analyzer I wrote several years ago.  My original Java program was developed using Kirchhoff and Therein approach to solving circuits.  

This new python program using a **Two-Port Network Analysis** using **Transmission Parameters** (or **ABCD Parameters**).

This is a python based program that provides similar functionality.

With this program you can:
1. Enter in the filter parameters (i.e. coupling shunt and coupling series pulling capacitors, Crystal motional parameters)
2. Adjust the starting and ending frequency to sweep the filter and generate a bode plot.  This allows you to see how the filter performs. You can also change filter parameters to see the effect on the filter.
3. Add termination at either end of the filter and generate a bode plot to see how the filter performs. 
4. Perform a Dishal/Hayward analysis to optimize the choice of the coupling capacitors based on the center frequency and bandwidth you desire.
5. You can also perform a termination analysis to determine the optimum termination to achieved designed insertion loss, passband ripple and/or carrier supression.
6. View the impact on a LSB or USB signal based on the BFO offset from the center frequency.  This allows you to predict the audio passband attenuation as well as the carries suppression (attenuation)  

Detailed documentation at  [Documentation](docs/FilterAnalyzerDocumentation.md)

Sample use of the program at [Sample Usage](FilterAnalyzerTutorial.md)
