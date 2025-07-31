function read_files(files){
  // Go through selected files and perform pre-processing for HTML files.
  explanationModal.style.display = "none"
  exploreModal.style.display = "none"
  processingModal.style.display = "block"
  
  var re = new RegExp('messages/.*message.*\.html');
  messages_array = []
  
  gtag('event', 'Load', {
      'event_category': 'Load',
      'event_label': 'Custom'})
  
  for (var i = 0; i < files.length; i++) {
    (function(file, i) {
      if (re.test(file.webkitRelativePath)){
        count_init += 1
        var reader = new FileReader()
        reader.onloadend = function(){
          try {
            // Parse HTML content
            var parser = new DOMParser();
            var doc = parser.parseFromString(reader.result, 'text/html');
            
            // Extract thread title
            var titleElement = doc.querySelector('h1');
            var thread_title = titleElement ? normalizeText(titleElement.textContent) : "Unknown Thread";
            
            // Extract participants
            var participants = [];
            var participantsSection = doc.querySelector('h2');
            if (participantsSection && participantsSection.textContent.includes('Participants:')) {
              var participantsText = participantsSection.textContent;
              var participantsMatch = participantsText.match(/Participants:\s*(.+)/);
              if (participantsMatch) {
                participants = participantsMatch[1].split(',').map(name => name.trim());
              }
            }
            
            var thread_info = {
              'is_still_participant': true, // Assume true for HTML files
              'thread_type': 'Regular',
              'thread': thread_title,
              'nb_participants': participants.length
            }
            
            // Extract messages
            var messageSections = doc.querySelectorAll('section._a6-g');
            
            for (var j = 0; j < messageSections.length; j++) {
              var section = messageSections[j];
              
              // Skip sections that are just participant info
              if (section.textContent.includes('Participants:')) {
                continue;
              }
              
              // Extract sender name from h2
              var senderElement = section.querySelector('h2');
              if (!senderElement) continue;
              
              var sender_name = normalizeText(senderElement.textContent);
              
              // Skip system messages
              if (sender_name.toLowerCase().includes('group invite link') || 
                  sender_name.toLowerCase().includes('participants:')) {
                continue;
              }
              
              // Extract message content
              var contentDiv = section.querySelector('div._2ph_._a6-p');
              if (!contentDiv) continue;
              
              var message_text = "";
              var contentDivs = contentDiv.querySelectorAll('div');
              for (var k = 0; k < contentDivs.length; k++) {
                var text = contentDivs[k].textContent.trim();
                if (text && !text.startsWith('❤') && !text.startsWith('👍') && !text.startsWith('😮')) {
                  message_text = normalizeText(text);
                  break;
                }
              }
              
              // Extract timestamp
              var footer = section.querySelector('footer');
              var timestamp = null;
              if (footer) {
                var timeDiv = footer.querySelector('div._a72d');
                if (timeDiv) {
                  var timestamp_str = timeDiv.textContent.trim();
                  timestamp = parseTimestamp(timestamp_str);
                }
              }
              
              // Create message object
              if (message_text && timestamp) {
                var message_info = {
                  'sender_name': sender_name,
                  'timestamp': timestamp / 1000, // Convert to seconds like original FBMessage
                  'type': 'Generic',
                  'media': 'None', // Could be enhanced to detect media
                  'message': message_text,
                  'length': message_text.length
                };
                
                messages_array.push(Object.assign({}, message_info, thread_info));
              }
            }
            
          } catch (e) {
            console.error("Error parsing HTML from file:", file.name, e);
          }
          
          count_end += 1 // Count the number of files that were processed
          if (count_init == count_end){ // If all files were processed, launch main program
            processingModal.style.display = "none"; // Hide processing modal on completion
            main()
          }
        }
        reader.readAsText(file)
      }
    })(files[i], i);
  }
}

function normalizeText(text) {
  if (!text) return "";
  
  try {
    // Handle HTML entities and normalize Unicode
    var tempDiv = document.createElement('div');
    tempDiv.innerHTML = text;
    text = tempDiv.textContent || tempDiv.innerText || "";
    
    // Basic Unicode normalization
    if (text.normalize) {
      text = text.normalize('NFKD');
    }
    
    return text.trim();
  } catch (e) {
    console.warn("Could not normalize text:", e);
    return String(text).trim();
  }
}

function parseTimestamp(timestamp_str) {
  try {
    timestamp_str = timestamp_str.trim();
    
    // Try multiple formats
    var formats = [
      /(\w{3}) (\d{1,2}), (\d{4}) (\d{1,2}):(\d{2}):(\d{2}) (am|pm)/i, // Oct 25, 2022 10:03:52 am
      /(\w+) (\d{1,2}), (\d{4}) (\d{1,2}):(\d{2}):(\d{2}) (am|pm)/i, // October 25, 2022 10:03:52 am
      /(\d{1,2})\/(\d{1,2})\/(\d{4}) (\d{1,2}):(\d{2}):(\d{2}) (am|pm)/i, // 10/25/2022 10:03:52 am
      /(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})/ // 2022-10-25 10:03:52
    ];
    
    var monthNames = {
      'jan': 0, 'january': 0, 'feb': 1, 'february': 1, 'mar': 2, 'march': 2,
      'apr': 3, 'april': 3, 'may': 4, 'jun': 5, 'june': 5,
      'jul': 6, 'july': 6, 'aug': 7, 'august': 7, 'sep': 8, 'september': 8,
      'oct': 9, 'october': 9, 'nov': 10, 'november': 10, 'dec': 11, 'december': 11
    };
    
    // Try first format (most common)
    var match = timestamp_str.match(formats[0]);
    if (match) {
      var month = monthNames[match[1].toLowerCase()];
      var day = parseInt(match[2]);
      var year = parseInt(match[3]);
      var hour = parseInt(match[4]);
      var minute = parseInt(match[5]);
      var second = parseInt(match[6]);
      var ampm = match[7].toLowerCase();
      
      if (ampm === 'pm' && hour !== 12) hour += 12;
      if (ampm === 'am' && hour === 12) hour = 0;
      
      var date = new Date(year, month, day, hour, minute, second);
      return date.getTime();
    }
    
    // Try other formats...
    for (var i = 1; i < formats.length; i++) {
      match = timestamp_str.match(formats[i]);
      if (match) {
        // Handle different format patterns...
        // For simplicity, try to parse with Date constructor
        var parsedDate = new Date(timestamp_str);
        if (!isNaN(parsedDate.getTime())) {
          return parsedDate.getTime();
        }
      }
    }
    
    console.warn("Could not parse timestamp:", timestamp_str);
    return Date.now(); // Fallback to current time
    
  } catch (e) {
    console.error("Error parsing timestamp:", timestamp_str, e);
    return Date.now();
  }
}
