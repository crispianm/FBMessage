function read_files_json(files){
  // Go through selected files and perform pre-processing for JSON files.
  explanationModal.style.display = "none"
  exploreModal.style.display = "none"
  processingModal.style.display = "block"
  
  var re = new RegExp('.*\.json$');
  messages_array = []
  
  gtag('event', 'Load', {
      'event_category': 'Load',
      'event_label': 'JSON Custom'})
  
  for (var i = 0; i < files.length; i++) {
    (function(file, i) {
      if (re.test(file.name) || re.test(file.webkitRelativePath)){
        count_init += 1
        var reader = new FileReader()
        reader.onloadend = function(){
          try {
            // Parse JSON content
            var jsonData = JSON.parse(reader.result);
            
            // Extract thread information
            var thread_title = jsonData.threadName || jsonData.thread_path || "Unknown Thread";
            var participants = jsonData.participants || [];
            
            var thread_info = {
              'is_still_participant': true,
              'thread_type': 'Regular',
              'thread': thread_title,
              'nb_participants': participants.length
            }
            
            // Extract messages
            var messages = jsonData.messages || [];
            
            for (var j = 0; j < messages.length; j++) {
              var msg = messages[j];
              
              // Skip unsent messages
              if (msg.isUnsent) {
                continue;
              }
              
              // Extract message content
              var message_text = msg.text || msg.content || "";
              if (!message_text && msg.media && msg.media.length > 0) {
                message_text = "[Media file]";
              }
              if (!message_text && msg.sticker) {
                message_text = "[Sticker]";
              }
              if (!message_text && msg.gifs && msg.gifs.length > 0) {
                message_text = "[GIF]";
              }
              
              // Skip empty messages
              if (!message_text) {
                continue;
              }
              
              // Extract timestamp - JSON format uses milliseconds
              var timestamp = msg.timestamp || msg.timestamp_ms || Date.now();
              
              // Extract sender name
              var sender_name = msg.senderName || msg.sender_name || "Unknown Sender";
              
              // Normalize text using the function defined in html-preprocessing.js
              message_text = normalizeTextJSON(message_text);
              sender_name = normalizeTextJSON(sender_name);
              
              // Create message object compatible with existing format
              var message_info = {
                'sender_name': sender_name,
                'timestamp': timestamp / 1000, // Convert to seconds like original FBMessage
                'type': 'Generic',
                'media': (msg.media && msg.media.length > 0) || msg.sticker || (msg.gifs && msg.gifs.length > 0) ? 'Media' : 'None',
                'message': message_text,
                'length': message_text.length,
                'reactions': msg.reactions || []
              };
              
              messages_array.push(Object.assign({}, message_info, thread_info));
            }
            
          } catch (e) {
            console.error("Error parsing JSON from file:", file.name, e);
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

function normalizeTextJSON(text) {
  // JSON-specific text normalization (duplicate of HTML version for reliability)
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

function detectFileType(files) {
  // Detect whether we're dealing with HTML or JSON files
  var hasHTML = false;
  var hasJSON = false;
  
  for (var i = 0; i < files.length; i++) {
    var fileName = files[i].name.toLowerCase();
    var filePath = files[i].webkitRelativePath ? files[i].webkitRelativePath.toLowerCase() : fileName;
    
    if (fileName.endsWith('.html') || (filePath.includes('message') && fileName.endsWith('.html'))) {
      hasHTML = true;
    }
    if (fileName.endsWith('.json')) {
      hasJSON = true;
    }
  }
  
  return { hasHTML: hasHTML, hasJSON: hasJSON };
}

function read_files_unified(files) {
  // Unified function to handle both HTML and JSON files
  var fileTypes = detectFileType(files);
  
  if (fileTypes.hasJSON && fileTypes.hasHTML) {
    alert("Please upload either HTML files OR JSON files, not both types together.");
    return;
  }
  
  if (fileTypes.hasJSON) {
    console.log("Detected JSON files - using JSON processor");
    read_files_json(files);
  } else if (fileTypes.hasHTML) {
    console.log("Detected HTML files - using HTML processor");
    read_files(files); // Call the existing HTML processor
  } else {
    alert("No valid message files found. Please upload Facebook message HTML files or JSON files.");
  }
}
