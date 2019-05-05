# Copyright 2017 Rob Alexander

# Licence is 3-clause BSD (https://opensource.org/licenses/BSD-3-Clause):

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import random, statistics

Roll3d6Probabilities = [0,0,0,0.5,1.38,2.77,4.62,6.94,9.72,11.57,12.50,12.50,11.57,9.72,6.94,4.62,2.77,1.38,0.5]
Flat3d6Probabilities = [0,0,0] + [(100/16)] * 16

#do a quick test that distro is complete
cumulative = 0
for prob in Flat3d6Probabilities:
    cumulative += prob
#print(cumulative)


## Functions for rolling dice
def randomStatFromDistribution(distro):
    #assumption - distro gives non-cum probabilities for values 0 and upwards in order
    #print(len(distro), len(distro))
    return random.choices(range(len(distro)), distro)[0] #error saying that "choices" does not exist means you're running Python pre-3.6

def roll3d6InOrderDieByDie():
    character = []
    for attrib in range(6):
        roll = 0
        for die in range(3):
            roll += random.randint(1,6)
        character = character + [roll]
    return character

def roll3d6InOrderUsingDistro():
    character = []
    for attrib in range(6):
        roll = 0        
        character = character + [randomStatFromDistribution(Roll3d6Probabilities)]
    #print(character)
    return character

def roll3d6InOrderUsingFlatDistro():
    character = []
    for attrib in range(6):
        roll = 0        
        character = character + [randomStatFromDistribution(Flat3d6Probabilities)]
    return character

def meanAttribute(character):
    return sum(character)/len(character)

def getBECMIModifier(attribValue):
    BECMIModifiers = [-99,-99,-99,-3,-2,-2,-1,-1,-1,0,0,0,0,1,1,1,2,2,3]
    return BECMIModifiers[attribValue]

def getSWNModifier(attribValue):
    SWNModifiers = [-99,-99,-99,-2,-1,-1,-1,-1,0,0,0,0,0,0,1,1,1,1,2]
    return SWNModifiers[attribValue]
    

def sumModifiers(character, modifierLookupFunction):
    modTotal = 0
    for attrib in character:   #TODO: use a list comprehension to do this
        modTotal += modifierLookupFunction(attrib)
    return modTotal

def sumModifiersBECMI(character):
    return sumModifiers(character, getBECMIModifier)    


### Validity rules
def anythingGoes(character, attributeModifierRule):
    return True

def averageAttribTotal(character, attributeModifierRule):
    return sum(character) == 63 #total is mean for 18d6

def averageSumOfModifiersRaw(character, attributeModifierRule):
    return sumModifiers(character, attributeModifierRule) == 0

def averageSumOfModifiersLotFP(character, attributeModifierRule):
    #Average LotFP-valid character has +1.5 sum-of-mod, so approximate that
    #Alternative (less variation in accepted characters) would be just
    #to accept either 1 or 2, not both
    #If set to 1, this slightly worse than LotFP, so could offer players gamble of this or actually rolling for themselves
    sm = sumModifiers(character, attributeModifierRule) 
    return (sm==1 or sm==2)

#impose the current Immergleich rule
def averageSumOfModifiersIs2(character, attributeModifierRule):
    sm = sumModifiers(character, attributeModifierRule) 
    return (sm==2)

def LotFPCompliantSumOfModifiers(character, attributeModifierRule):
    return sumModifiers(character, attributeModifierRule) >= 0 


### Functions that do the rolling process itself
def rollCharacterUntilCondition(characterRollFunction, attributeModifierRule, characterValidityRule):
    character = characterRollFunction()

    while (not characterValidityRule(character, attributeModifierRule)):
        character = characterRollFunction()

    return character

def makeCharacters(number, characterRollRule, attributeModifierRule, characterValidityRule):
    print("Making", number, "characters using", characterValidityRule.__name__)
    characters = []
    for c in range(number):
        characters += [rollCharacterUntilCondition(characterRollRule, attributeModifierRule, characterValidityRule)]
    return characters


def charAsRawValueString(c):
    return f"{c} \t\t {sumModifiersBECMI(c)}, {meanAttribute(c):10.4}"

def charAsModifierOnlyString(c, attributeModifierRule):
    charMods = [attributeModifierRule(a) for a in c]
    return f"{charMods} \t\t {sumModifiersBECMI(c)}, {meanAttribute(c):10.4}"

def printCharacters(characters, characterPrinter):
    allAttributes = []
    #count through characters with index so we can number them in the printout
    for i in range(0, len(characters)):
       c=characters[i]
       allAttributes += c       
       print(i, "---", characterPrinter(c))

    charmods = list(map(sumModifiersBECMI, characters)) #TODO: make parameterised on modifier tupe
    print("Mean character mod: ", "{0:.2f}".format(sum(charmods)/len(charmods)))

    print("Mean attribute value: ", "{0:.1f}".format(sum(allAttributes)/len(allAttributes)))

    print("Std dev attribute value: ", "{0:.2f}".format(statistics.stdev(allAttributes)))

    print("Prop of 3", "{0:.5f}".format(allAttributes.count(3)/len(allAttributes)))
    print("Prop of 18", "{0:.5f}".format(allAttributes.count(18)/len(allAttributes)))



if __name__ == '__main__':
    characters = makeCharacters(10, roll3d6InOrderDieByDie, getBECMIModifier, averageSumOfModifiersIs2)

    printCharacters(characters, charAsRawValueString)

