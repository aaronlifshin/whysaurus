export const titleMaxCharacterCount = 200;

export function validateTitle(title){
  if (!title || title.trim() === '') {
    // Disabling this warning for now bc our logic for disabling the publish button is taking care of it, 
    // and our WIP logic for displaying the feedback area is making this flash in a distracting way -JF 
    //   return "This claim doesn't seem to have any words.";
    return "";
  } else if (title.length > titleMaxCharacterCount){
    return "This is over the character limit. Try dividing your idea into multiple claims. Remember: brevity is the soul of wit!";
  } else {
    return null;
  }
}
