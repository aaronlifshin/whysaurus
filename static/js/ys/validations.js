export const titleMaxCharacterCount = 200;

export function validateTitle(title){
  if (!title || title.trim() === '') {
    return 'Point text is required.';
  } else if (title.length > titleMaxCharacterCount){
    return 'Point text too long.';
  } else {
    return null;
  }
}
