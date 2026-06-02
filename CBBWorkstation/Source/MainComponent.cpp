#include "MainComponent.h"

#include "Engine/ChordParser.h"

MainComponent::MainComponent()
{
    titleLabel.setText("ChordFlow Workstation", juce::dontSendNotification);
    titleLabel.setFont(juce::FontOptions(28.0f, juce::Font::bold));
    titleLabel.setJustificationType(juce::Justification::centredLeft);
    addAndMakeVisible(titleLabel);

    subtitleLabel.setText("Turn chord progressions into practice-ready backing tracks", juce::dontSendNotification);
    subtitleLabel.setJustificationType(juce::Justification::centredLeft);
    addAndMakeVisible(subtitleLabel);

    styleLabel.setText("Backing Style", juce::dontSendNotification);
    styleLabel.setJustificationType(juce::Justification::centredLeft);
    addAndMakeVisible(styleLabel);

    styleSelector.addItem("Pop", static_cast<int>(StyleType::Pop) + 1);
    styleSelector.addItem("J-Pop", static_cast<int>(StyleType::JPop) + 1);
    styleSelector.addItem("Blues", static_cast<int>(StyleType::Blues) + 1);
    styleSelector.addItem("Ballad", static_cast<int>(StyleType::Ballad) + 1);
    styleSelector.setSelectedId(static_cast<int>(StyleType::Pop) + 1);
    styleSelector.onChange = [this] { refreshGeneratedPreview(); };
    addAndMakeVisible(styleSelector);

    generationLabel.setJustificationType(juce::Justification::centredLeft);
    generationLabel.setColour(juce::Label::textColourId, juce::Colour::fromRGB(200, 208, 216));
    addAndMakeVisible(generationLabel);

    addAndMakeVisible(chordInputComponent);
    addAndMakeVisible(sectionPanelComponent);
    addAndMakeVisible(grooveControlComponent);
    addAndMakeVisible(transportComponent);

    chordInputComponent.setOnChordChange([this] { refreshGeneratedPreview(); });
    sectionPanelComponent.setOnSectionChange([this](SectionType) { refreshGeneratedPreview(); });
    grooveControlComponent.setOnGrooveChange([this] { refreshGeneratedPreview(); });
    transportComponent.setOnPlay([this]
    {
        const auto parsedProgression = Engine::ChordParser::parse(chordInputComponent.getChordText());
        if (! parsedProgression.isValid)
        {
            transportComponent.setStatusText(parsedProgression.message);
            return;
        }

        const auto generatedPattern = patternGenerator.prepare(parsedProgression.chords,
                                                               getSelectedStyle(),
                                                               sectionPanelComponent.getSelectedSection(),
                                                               grooveControlComponent.getEnergy(),
                                                               grooveControlComponent.getSwing());

        playbackEngine.play(generatedPattern.description, transportComponent.isLoopEnabled());
        auto statusText = "Playing: " + generatedPattern.description;
        if (playbackEngine.isLoopEnabled())
            statusText += " / Loop";
        transportComponent.setStatusText(statusText);
    });
    transportComponent.setOnStop([this]
    {
        playbackEngine.stop();
        transportComponent.setStatusText("Stopped");
    });

    setSize(1120, 840);
    refreshGeneratedPreview();
}

void MainComponent::paint(juce::Graphics& g)
{
    g.fillAll(juce::Colour::fromRGB(20, 24, 30));

    auto area = getLocalBounds().reduced(24);
    g.setColour(juce::Colour::fromRGB(34, 40, 50));
    g.fillRoundedRectangle(area.toFloat(), 18.0f);

    g.setColour(juce::Colour::fromRGB(54, 62, 76));
    g.drawRoundedRectangle(area.toFloat(), 18.0f, 2.0f);
}

void MainComponent::resized()
{
    auto area = getLocalBounds().reduced(32);

    auto header = area.removeFromTop(76);
    titleLabel.setBounds(header.removeFromTop(34));
    subtitleLabel.setBounds(header.removeFromTop(22));

    auto styleArea = area.removeFromTop(60);
    styleLabel.setBounds(styleArea.removeFromLeft(160));
    styleSelector.setBounds(styleArea.removeFromLeft(240).reduced(0, 8));
    styleArea.removeFromLeft(20);
    generationLabel.setBounds(styleArea);

    area.removeFromTop(12);
    chordInputComponent.setBounds(area.removeFromTop(104));

    area.removeFromTop(12);
    auto middleRow = area.removeFromTop(240);
    sectionPanelComponent.setBounds(middleRow.removeFromLeft(middleRow.proportionOfWidth(0.48f)));
    middleRow.removeFromLeft(16);
    grooveControlComponent.setBounds(middleRow);

    area.removeFromTop(12);
    transportComponent.setBounds(area.removeFromTop(130));
}

void MainComponent::refreshGeneratedPreview()
{
    const auto parsedProgression = Engine::ChordParser::parse(chordInputComponent.getChordText());

    if (! parsedProgression.isValid)
    {
        generationLabel.setText(parsedProgression.message, juce::dontSendNotification);
        if (! playbackEngine.isPlaying())
            transportComponent.setStatusText("Ready");
        return;
    }

    const auto generatedPattern = patternGenerator.prepare(parsedProgression.chords,
                                                           getSelectedStyle(),
                                                           sectionPanelComponent.getSelectedSection(),
                                                           grooveControlComponent.getEnergy(),
                                                           grooveControlComponent.getSwing());

    generationLabel.setText("Preview: " + generatedPattern.drumPattern + " / " + generatedPattern.bassPattern,
                            juce::dontSendNotification);

    if (! playbackEngine.isPlaying())
        transportComponent.setStatusText(generatedPattern.description);
}

StyleType MainComponent::getSelectedStyle() const noexcept
{
    const auto selected = styleSelector.getSelectedId() - 1;
    if (selected < 0)
        return StyleType::Pop;

    return static_cast<StyleType>(selected);
}
