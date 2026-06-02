#include "GrooveControlComponent.h"

GrooveControlComponent::GrooveControlComponent()
{
    titleLabel.setText("Groove Controls", juce::dontSendNotification);
    titleLabel.setJustificationType(juce::Justification::centredLeft);
    titleLabel.setFont(juce::FontOptions(20.0f, juce::Font::bold));
    addAndMakeVisible(titleLabel);

    energyLabel.setText("Energy", juce::dontSendNotification);
    swingLabel.setText("Swing", juce::dontSendNotification);
    addAndMakeVisible(energyLabel);
    addAndMakeVisible(swingLabel);

    configureSlider(energySlider);
    configureSlider(swingSlider);
    addAndMakeVisible(energySlider);
    addAndMakeVisible(swingSlider);

    energySlider.onValueChange = [this]
    {
        if (onGrooveChange != nullptr)
            onGrooveChange();
    };

    swingSlider.onValueChange = [this]
    {
        if (onGrooveChange != nullptr)
            onGrooveChange();
    };
}

void GrooveControlComponent::paint(juce::Graphics& g)
{
    g.setColour(juce::Colour::fromRGB(44, 51, 64));
    g.fillRoundedRectangle(getLocalBounds().toFloat(), 18.0f);
}

void GrooveControlComponent::resized()
{
    auto area = getLocalBounds().reduced(24);
    titleLabel.setBounds(area.removeFromTop(28));
    area.removeFromTop(16);

    auto firstRow = area.removeFromTop(52);
    energyLabel.setBounds(firstRow.removeFromLeft(90));
    energySlider.setBounds(firstRow);

    area.removeFromTop(18);
    auto secondRow = area.removeFromTop(52);
    swingLabel.setBounds(secondRow.removeFromLeft(90));
    swingSlider.setBounds(secondRow);
}

void GrooveControlComponent::configureSlider(juce::Slider& slider)
{
    slider.setSliderStyle(juce::Slider::LinearHorizontal);
    slider.setTextBoxStyle(juce::Slider::NoTextBox, false, 0, 0);
    slider.setRange(0.0, 1.0, 0.01);
    slider.setValue(0.5);
}

float GrooveControlComponent::getEnergy() const noexcept
{
    return static_cast<float>(energySlider.getValue());
}

float GrooveControlComponent::getSwing() const noexcept
{
    return static_cast<float>(swingSlider.getValue());
}

void GrooveControlComponent::setOnGrooveChange(std::function<void()> callback)
{
    onGrooveChange = std::move(callback);
}
