from videoGen import generate_video

# Test with a simple prompt
#success = generate_video("Set in a desolate post-apocalyptic Earth, where crumbled skyscrapers pierce the darkened sky and ash falls like snow, Chantal—a resilient young woman with curly dark hair, a leather jacket, and an artistic spirit—stands at the edge of an abandoned city. In her hands, she clutches a battered sketchbook, her last link to the beauty of the world that once was. Suddenly, a faint blue glow illuminates the ruins. Emerging from the shadows is an alien figure, tall and otherworldly, with translucent skin that shifts colors like a living nebula and glowing, empathetic eyes.The alien cautiously approaches Chantal, extending a hand with a device projecting holograms of its dying home planet. Chantal, hesitant at first, realizes the alien is an artist like her—its holograms depict fantastical creatures, intricate designs, and a vibrant world lost to catastrophe. They communicate wordlessly through their art, drawing symbols and images in the ash-covered ground, bridging their worlds through creativity. The scene ends with Chantal and the alien standing together beneath the eerie green hue of an aurora caused by Earth's fractured atmosphere, the alien offering a small, glowing artifact as a gesture of friendship. Chantal smiles, hope flickering in her eyes for the first time in years")
success = generate_video("You make your way to the old church at the edge of town, its silhouette looming in the fog. The creaking door reveals an eerie silence, broken only by the faint sound of footsteps echoing from within. A figure dressed in white robes emerges, their face glowing in the moonlight. 'You shouldn't be here,' they mutter, their voice trembling with a mix of fear and urgency. Gender: she/her Skin colour: fair Eye colour: black Hair: Long, dark black hair. Outfit: long, flowy white dress. very dreamy Accessories: a pet rabbit Expressions: serene")

if success:
    print("Video generated successfully!")
else:
    print("Video generation failed!")

