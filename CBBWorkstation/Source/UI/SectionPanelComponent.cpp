#include "SectionPanelComponent.h"

SectionPanelComponent::SectionPanelComponent()
{
    titleLabel.setText("Playback Section", juce::dontSendNotification);
    titleLabel.setJustificationType(juce::Justification::centredLeft);
    titleLabel.setFont(juce::FontOptions(20.0f, juce::Font::bold));
    addAndMakeVisible(titleLabel);

    for (auto* button : { &mainAButton, &fillButton, &endingButton })
    {
        button->setRadioGroupId(1);
        addAndMakeVisible(*button);
    }

    mainAButton.setToggleState(true, juce::dontSendNotification);
    mainAButton.onClick = [this] { selectSection(SectionType::MainA); };
    fillButton.onClick = [this] { selectSection(SectionType::Fill); };
    endingButton.onClick = [this] { selectSection(SectionType::Ending); };
}

void SectionPanelComponent::paint(juce::Graphics& g)
{
    g.setColour(juce::Colour::fromRGB(44, 51, 64));
    g.fillRoundedRectangle(getLocalBounds().toFloat(), 18.0f);
}

void SectionPanelComponent::resized()
{
    auto area = getLocalBounds().reduced(24);
    titleLabel.setBounds(area.removeFromTop(28));
    area.removeFromTop(16);

    const auto buttonGap = 10;
    const auto buttonWidth = (area.getWidth() - buttonGap * 2) / 3;
    mainAButton.setBounds(area.removeFromLeft(buttonWidth));
    area.removeFromLeft(buttonGap);
    fillButton.setBounds(area.removeFromLeft(buttonWidth));
    area.removeFromLeft(buttonGap);
    endingButton.setBounds(area.removeFromLeft(buttonWidth));
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
