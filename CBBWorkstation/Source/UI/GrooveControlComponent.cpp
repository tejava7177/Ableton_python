#include "GrooveControlComponent.h"

GrooveControlComponent::GrooveControlComponent()
{
    titleLabel.setText("Groove Controls", juce::dontSendNotification);
    titleLabel.setJustificationType(juce::Justification::centredLeft);
    addAndMakeVisible(titleLabel);

    energyLabel.setText("Energy", juce::dontSendNotification);
    swingLabel.setText("Swing", juce::dontSendNotification);
    addAndMakeVisible(energyLabel);
    addAndMakeVisible(swingLabel);

    configureSlider(energySlider);
    configureSlider(swingSlider);
    addAndMakeVisible(energySlider);
    addAndMakeVisible(swingSlider);
}

void GrooveControlComponent::paint(juce::Graphics& g)
{
    g.setColour(juce::Colour::fromRGB(42, 48, 60));
    g.fillRoundedRectangle(getLocalBounds().toFloat(), 14.0f);
}

void GrooveControlComponent::resized()
{
    auto area = getLocalBounds().reduced(20);
    titleLabel.setBounds(area.removeFromTop(24));
    area.removeFromTop(12);

    auto firstRow = area.removeFromTop(52);
    energyLabel.setBounds(firstRow.removeFromLeft(80));
    energySlider.setBounds(firstRow);

    area.removeFromTop(18);
    auto secondRow = area.removeFromTop(52);
    swingLabel.setBounds(secondRow.removeFromLeft(80));
    swingSlider.setBounds(secondRow);
}

void GrooveControlComponent::configureSlider(juce::Slider& slider)
{
    slider.setSliderStyle(juce::Slider::LinearHorizontal);
    slider.setTextBoxStyle(juce::Slider::TextBoxRight, false, 60, 24);
    slider.setRange(0.0, 1.0, 0.01);
    slider.setValue(0.5);
}

