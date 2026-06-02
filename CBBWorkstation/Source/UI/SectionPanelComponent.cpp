#include "SectionPanelComponent.h"

SectionPanelComponent::SectionPanelComponent()
{
    titleLabel.setText("Song Sections", juce::dontSendNotification);
    titleLabel.setJustificationType(juce::Justification::centredLeft);
    addAndMakeVisible(titleLabel);

    for (auto* button : { &mainAButton, &fillButton, &endingButton })
    {
        addAndMakeVisible(*button);
    }

    mainAButton.setToggleState(true, juce::dontSendNotification);
    mainAButton.onClick = [this] { selectSection(SectionType::MainA); };
    fillButton.onClick = [this] { selectSection(SectionType::Fill); };
    endingButton.onClick = [this] { selectSection(SectionType::Ending); };
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

SectionType SectionPanelComponent::getSelectedSection() const noexcept
{
    if (fillButton.getToggleState())
        return SectionType::Fill;

    if (endingButton.getToggleState())
        return SectionType::Ending;

    return SectionType::MainA;
}

void SectionPanelComponent::setOnSectionChange(std::function<void(SectionType)> callback)
{
    onSectionChange = std::move(callback);
}

void SectionPanelComponent::selectSection(SectionType section)
{
    mainAButton.setToggleState(section == SectionType::MainA, juce::dontSendNotification);
    fillButton.setToggleState(section == SectionType::Fill, juce::dontSendNotification);
    endingButton.setToggleState(section == SectionType::Ending, juce::dontSendNotification);

    if (onSectionChange != nullptr)
        onSectionChange(section);
}
