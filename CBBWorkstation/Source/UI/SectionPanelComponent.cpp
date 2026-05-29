#include "SectionPanelComponent.h"

SectionPanelComponent::SectionPanelComponent()
{
    titleLabel.setText("Song Sections", juce::dontSendNotification);
    titleLabel.setJustificationType(juce::Justification::centredLeft);
    addAndMakeVisible(titleLabel);

    for (auto* button : { &mainAButton, &fillButton, &endingButton })
    {
        button->setClickingTogglesState(true);
        addAndMakeVisible(*button);
    }

    mainAButton.setToggleState(true, juce::dontSendNotification);
}

void SectionPanelComponent::paint(juce::Graphics& g)
{
    g.setColour(juce::Colour::fromRGB(42, 48, 60));
    g.fillRoundedRectangle(getLocalBounds().toFloat(), 14.0f);
}

void SectionPanelComponent::resized()
{
    auto area = getLocalBounds().reduced(20);
    titleLabel.setBounds(area.removeFromTop(24));
    area.removeFromTop(16);

    const auto buttonHeight = 40;
    mainAButton.setBounds(area.removeFromTop(buttonHeight));
    area.removeFromTop(10);
    fillButton.setBounds(area.removeFromTop(buttonHeight));
    area.removeFromTop(10);
    endingButton.setBounds(area.removeFromTop(buttonHeight));
}

