/**
 * Main Application Component
 * Single-page interface for NCERT Science learning platform
 * Features: Topic selection, Summary, Chat Q&A, Quiz generation, Image upload, Evaluation
 */
import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  // State management
  const [classes, setClasses] = useState([])
  const [topics, setTopics] = useState([])
  const [selectedClass, setSelectedClass] = useState('')
  const [selectedTopic, setSelectedTopic] = useState(null)
  const [summary, setSummary] = useState(null)
  const [messages, setMessages] = useState([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [inputMessage, setInputMessage] = useState('')
  const [quiz, setQuiz] = useState(null)
  const [quizAnswers, setQuizAnswers] = useState({})
  const [evaluation, setEvaluation] = useState(null)
  const [loading, setLoading] = useState(false)
  const [loadingClasses, setLoadingClasses] = useState(true)
  const [loadingTopics, setLoadingTopics] = useState(false)
  const [error, setError] = useState(null)
  const [uploadedImageText, setUploadedImageText] = useState('')
  const [uploadedFile, setUploadedFile] = useState(null)
  const fileInputRef = useRef(null)
  
  const messagesEndRef = useRef(null)
  const chatInputRef = useRef(null)

  // Scroll to bottom of chat
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Load classes and topics on mount
  useEffect(() => {
    loadClasses()
  }, [])

  // Load topics when class changes
  useEffect(() => {
    if (selectedClass) {
      loadTopics(selectedClass)
    }
  }, [selectedClass])

  /**
   * Load available class levels
   */
  const loadClasses = async () => {
    setLoadingClasses(true)
    setError(null)
    try {
      console.log('Loading classes from:', `${API_BASE_URL}/api/topics/classes`)
      const response = await axios.get(`${API_BASE_URL}/api/topics/classes`)
      console.log('Classes loaded:', response.data)
      setClasses(response.data)
      if (response.data && response.data.length > 0) {
        setSelectedClass(response.data[0])
      } else {
        setError('No classes available. Please check backend connection.')
      }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to load classes'
      setError(`Failed to load classes: ${errorMsg}. Check if backend is running at ${API_BASE_URL}`)
      console.error('Error loading classes:', err)
      console.error('Full error:', err.response || err)
    } finally {
      setLoadingClasses(false)
    }
  }

  /**
   * Load topics for selected class
   */
  const loadTopics = async (classLevel) => {
    if (!classLevel) return
    
    setLoadingTopics(true)
    setError(null)
    try {
      console.log('Loading topics for class:', classLevel)
      const response = await axios.get(`${API_BASE_URL}/api/topics/`, {
        params: { class_level: classLevel }
      })
      console.log('Topics loaded:', response.data)
      setTopics(response.data || [])
      // Clear selected topic when class changes
      setSelectedTopic(null)
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to load topics'
      setError(`Failed to load topics: ${errorMsg}`)
      console.error('Error loading topics:', err)
      console.error('Full error:', err.response || err)
      setTopics([])
    } finally {
      setLoadingTopics(false)
    }
  }

  /**
   * Handle topic selection
   */
  const handleTopicSelect = (topic) => {
    setSelectedTopic(topic)
    setSummary(null)
    setMessages([])
    setQuiz(null)
    setQuizAnswers({})
    setEvaluation(null)
    setUploadedImageText('')
    setUploadedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  /**
   * Generate and load summary for selected topic
   */
  const handleGenerateSummary = async () => {
    if (!selectedTopic) return
    
    const summaryMessageId = Date.now()
    setLoading(true)
    setIsStreaming(true)
    setError(null)
    
    // Add user message and loading assistant message
    const userMessage = {
      id: Date.now() - 1,
      role: 'user',
      content: 'Generate summary'
    }
    const loadingMessage = {
      id: summaryMessageId,
      role: 'assistant',
      content: '',
      type: 'summary'
    }
    setMessages(prev => [...prev, userMessage, loadingMessage])
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/summary/`, {
        topic_id: selectedTopic.topic_id,
        topic_name: selectedTopic.topic_name,
        class_level: selectedTopic.class_level
      })
      setSummary(response.data)
      
      // Update the loading message with summary
      setMessages(prev => prev.map(msg => 
        msg.id === summaryMessageId 
          ? {
              ...msg,
              content: `**"${selectedTopic.topic_name}":**\n\n${response.data.summary}\n\n** **\n${response.data.key_points.map((p, i) => `${i+1}. ${p}`).join('\n')}`
            }
          : msg
      ))
    } catch (err) {
      setError('Failed to generate summary')
      console.error(err)
      setMessages(prev => prev.map(msg => 
        msg.id === summaryMessageId 
          ? { ...msg, content: 'Sorry, failed to generate summary. Please try again.' }
          : msg
      ))
    } finally {
      setLoading(false)
      setIsStreaming(false)
    }
  }

  /**
   * Send chat message with streaming response
   */
  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!inputMessage.trim() || !selectedTopic) return
    
    const userMessage = { id: Date.now(), role: 'user', content: inputMessage.trim() }
    const updatedMessages = [...messages, userMessage]
    setMessages(updatedMessages)
    setInputMessage('')
    setLoading(true)
    setIsStreaming(true)
    
    // Add placeholder assistant message for streaming
    const assistantMessageId = Date.now() + 1
    setMessages([...updatedMessages, {
      id: assistantMessageId,
      role: 'assistant',
      content: ''
    }])
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic_id: selectedTopic.topic_id,
          topic_name: selectedTopic.topic_name,
          class_level: selectedTopic.class_level,
          messages: updatedMessages.map(m => ({ role: m.role, content: m.content }))
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let accumulatedContent = ''
      
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              if (data.error) {
                throw new Error(data.error)
              }
              
              if (data.chunk) {
                // Append chunk to accumulated content
                accumulatedContent += data.chunk
                
                // Update the assistant message with accumulated content
                setMessages(prevMessages => 
                  prevMessages.map(msg => 
                    msg.id === assistantMessageId 
                      ? { ...msg, content: accumulatedContent }
                      : msg
                  )
                )
              }
              
              if (data.done) {
                // Final update with full response and sources
                setMessages(prevMessages => 
                  prevMessages.map(msg => 
                    msg.id === assistantMessageId 
                      ? { ...msg, content: data.full_response, sources: data.sources }
                      : msg
                  )
                )
                setIsStreaming(false)
              }
            } catch (parseError) {
              console.error('Error parsing SSE data:', parseError)
            }
          }
        }
      }
    } catch (err) {
      setError('Failed to get response')
      console.error(err)
      // Update the assistant message with error
      setMessages(prevMessages => 
        prevMessages.map(msg => 
          msg.id === assistantMessageId 
            ? { ...msg, content: 'Sorry, I encountered an error. Please try again.' }
            : msg
        ).filter(msg => msg.id !== assistantMessageId || msg.content)
      )
    } finally {
      setLoading(false)
      setIsStreaming(false)
    }
  }

  /**
   * Generate quiz
   */
  const handleGenerateQuiz = async () => {
    if (!selectedTopic) return
    
    const quizMessageId = Date.now()
    setLoading(true)
    setIsStreaming(true)
    setError(null)
    
    // Add user message and loading assistant message
    const userMessage = {
      id: Date.now() - 1,
      role: 'user',
      content: 'Generate quiz'
    }
    const loadingMessage = {
      id: quizMessageId,
      role: 'assistant',
      content: '',
      type: 'quiz'
    }
    setMessages(prev => [...prev, userMessage, loadingMessage])
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/quiz/`, {
        topic_id: selectedTopic.topic_id,
        topic_name: selectedTopic.topic_name,
        class_level: selectedTopic.class_level,
        num_mcqs: 5,
        num_fill_blank: 3,
        num_short_answer: 2
      })
      setQuiz(response.data)
      setQuizAnswers({})
      setEvaluation(null)
      setUploadedFile(null)
      setUploadedImageText('')
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
      
      // Update the loading message with quiz and store quiz ID
      setMessages(prev => prev.map(msg => 
        msg.id === quizMessageId 
          ? {
              ...msg,
              content: '',
              quizData: response.data
            }
          : msg
      ))
    } catch (err) {
      setError('Failed to generate quiz')
      console.error(err)
      setMessages(prev => prev.map(msg => 
        msg.id === quizMessageId 
          ? { ...msg, content: 'Sorry, failed to generate quiz. Please try again.' }
          : msg
      ))
    } finally {
      setLoading(false)
      setIsStreaming(false)
    }
  }

  /**
   * Handle quiz answer input
   */
  const handleQuizAnswerChange = (questionId, answer) => {
    setQuizAnswers({
      ...quizAnswers,
      [questionId]: answer
    })
  }

  /**
   * Handle image upload for quiz answers
   */
  const handleImageUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    
    // Store the file
    setUploadedFile(file)
    setLoading(true)
    setError(null)
    
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await axios.post(
        `${API_BASE_URL}/api/evaluation/upload-image`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )
      
      setUploadedImageText(response.data.extracted_text)
      
      // Try to auto-fill quiz answers from OCR text
      // This is a simple implementation - you might want to enhance it
      const quizToUse = quiz || messages.find(m => m.quizData)?.quizData
      if (quizToUse) {
        const lines = response.data.extracted_text.split('\n').filter(l => l.trim())
        quizToUse.questions.forEach((q, index) => {
          if (lines[index]) {
            handleQuizAnswerChange(q.question_id, lines[index].trim())
          }
        })
      }
    } catch (err) {
      setError('Failed to process image')
      console.error(err)
      setUploadedFile(null) // Clear file on error
    } finally {
      setLoading(false)
    }
  }

  /**
   * Clear uploaded image
   */
  const handleClearImage = () => {
    setUploadedFile(null)
    setUploadedImageText('')
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  /**
   * Submit quiz for evaluation
   */
  const handleSubmitQuiz = async (quizId = null) => {
    const quizToUse = quizId ? 
      messages.find(m => m.quizData && m.quizData.quiz_id === quizId)?.quizData : 
      quiz
    
    if (!quizToUse) return
    
    // Need either answers or an image
    if (Object.keys(quizAnswers).length === 0 && !uploadedFile) return
    
    setLoading(true)
    setError(null)
    
    try {
      // Always use FormData for consistency
      const formData = new FormData()
      formData.append('quiz_id', quizToUse.quiz_id)
      formData.append('answers', JSON.stringify(quizAnswers))
      
      // Add file if uploaded
      if (uploadedFile) {
        formData.append('file', uploadedFile)
      }
      
      const response = await axios.post(
        `${API_BASE_URL}/api/evaluation/evaluate`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )
      
      setEvaluation(response.data)
      
      // Update the message with evaluation
      setMessages(prev => prev.map(msg => 
        msg.quizData && msg.quizData.quiz_id === quizToUse.quiz_id
          ? { ...msg, evaluation: response.data }
          : msg
      ))
    } catch (err) {
      setError('Failed to evaluate quiz')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>📚 NCERT Science Learning Platform</h1>
        <p>Classes 8-10 • Interactive Learning • Quiz & Evaluation</p>
      </header>

      <div className="app-container">
        {/* Left Sidebar - Topic Selection */}
        <aside className="sidebar">
          <div className="sidebar-section">
            <h2>Select Class</h2>
            {loadingClasses ? (
              <div className="loading-text">Loading classes...</div>
            ) : (
              <select
                value={selectedClass}
                onChange={(e) => {
                  console.log('Class changed to:', e.target.value)
                  setSelectedClass(e.target.value)
                }}
                className="select-input"
                disabled={classes.length === 0}
              >
                {classes.length === 0 ? (
                  <option value="">No classes available</option>
                ) : (
                  <>
                    <option value="" disabled>Select a class</option>
                    {classes.map(cls => (
                      <option key={cls} value={cls}>{cls}</option>
                    ))}
                  </>
                )}
              </select>
            )}
          </div>

          <div className="sidebar-section topics_div">
            <h2>Select Topic</h2>
            {loadingTopics ? (
              <div className="loading-text">Loading topics...</div>
            ) : topics.length === 0 ? (
              <div className="no-topics-message">
                {selectedClass ? 'No topics found. Try selecting a different class.' : 'Please select a class first.'}
              </div>
            ) : (
              <div className="topics-list">
                {topics.map(topic => (
                  <button
                    key={topic.topic_id}
                    onClick={() => {
                      console.log('Topic selected:', topic)
                      handleTopicSelect(topic)
                    }}
                    className={`topic-button ${selectedTopic?.topic_id === topic.topic_id ? 'active' : ''}`}
                  >
                    {topic.topic_name}
                  </button>
                ))}
              </div>
            )}
          </div>

        </aside>

        {/* Main Content Area - Chat Interface */}
        <main className="main-content">
          {error && (
            <div className="error-message">
              {error}
              <button onClick={() => setError(null)}>×</button>
            </div>
          )}

          {/* Chat Messages - Always visible */}
          <div className="chat-container">
            <div className="messages">
              {messages.length === 0 && (
                <div className="welcome-message">
                  <div className="welcome-icon">📚</div>
                  <h3>{selectedTopic ? `Welcome to ${selectedTopic.topic_name}` : 'Welcome to NCERT Science Learning Platform'}</h3>
                  <p>{selectedTopic ? 'Start a conversation or generate a summary to get started' : 'Please select a class and topic to get started'}</p>
                </div>
              )}
              
              {messages.map((msg, idx) => (
                <div key={msg.id || idx} className={`message-wrapper ${msg.role}`}>
                  <div className="message-avatar">
                    {msg.role === 'user' ? '👤' : '🤖'}
                  </div>
                  <div className="message-container">
                    <div className={`message ${msg.role}`}>
                      {msg.quizData ? (
                        <div className="quiz-in-chat">
                          <div className="message-content">
                            <strong>📝 Quiz: {msg.quizData.topic_name}</strong>
                          </div>
                          <div className="quiz-questions-inline">
                            {msg.quizData.questions.map((q, qIdx) => (
                              <div key={q.question_id} className="quiz-question-inline">
                                <p className="question-text-inline">
                                  <strong>Q{qIdx + 1} ({q.question_type}):</strong> {q.question}
                                </p>
                                
                                {q.question_type === 'mcq' && q.options && (
                                  <div className="quiz-options-inline">
                                    {q.options.map((option, optIdx) => (
                                      <label key={optIdx} className="option-label-inline">
                                        <input
                                          type="radio"
                                          name={q.question_id}
                                          value={option}
                                          onChange={(e) => handleQuizAnswerChange(q.question_id, e.target.value)}
                                          checked={quizAnswers[q.question_id] === option}
                                        />
                                        {option}
                                      </label>
                                    ))}
                                  </div>
                                )}
                                
                                {(q.question_type === 'fill_blank' || q.question_type === 'short_answer') && (
                                  <textarea
                                    value={quizAnswers[q.question_id] || ''}
                                    onChange={(e) => handleQuizAnswerChange(q.question_id, e.target.value)}
                                    placeholder="Type your answer here..."
                                    className="answer-input-inline"
                                    rows={q.question_type === 'short_answer' ? 3 : 1}
                                  />
                                )}
                              </div>
                            ))}
                            
                            <div className="quiz-actions-inline">
                              {uploadedFile ? (
                                <div className="uploaded-file-display">
                                  <span className="file-name">{uploadedFile.name}</span>
                                  <button
                                    onClick={handleClearImage}
                                    className="clear-file-button"
                                    type="button"
                                    title="Remove file"
                                  >
                                    ✕
                                  </button>
                                </div>
                              ) : (
                                <label className="upload-button-inline">
                                  📷 Upload Handwritten Answers
                                  <input
                                    ref={fileInputRef}
                                    type="file"
                                    accept="image/*"
                                    onChange={handleImageUpload}
                                    style={{ display: 'none' }}
                                  />
                                </label>
                              )}
                              <button
                                onClick={() => handleSubmitQuiz(msg.quizData.quiz_id)}
                                className="submit-quiz-button-inline"
                                disabled={loading || (Object.keys(quizAnswers).length === 0 && !uploadedFile)}
                              >
                                ✅ Submit Quiz
                              </button>
                            </div>
                            
                            {(evaluation || msg.evaluation) && (() => {
                              const evalData = msg.evaluation || evaluation
                              return (
                                <div className="evaluation-inline">
                                  <h4>📊 Quiz Results</h4>
                                <div className="score-display-inline">
                                  <p>Score: {evalData.correct_count || 0}/{evalData.total_questions || 0} ({evalData.score_percentage ? evalData.score_percentage.toFixed(1) : 0}%)</p>
                                </div>
                                {evalData.question_results && evalData.question_results.length > 0 && (
                                  <div className="results-details-inline">
                                    {evalData.question_results.map((result, rIdx) => (
                                      <div key={rIdx} className={`result-item-inline ${result.is_correct ? 'correct' : 'incorrect'}`}>
                                        <p><strong>Q{rIdx + 1}:</strong> {result.is_correct ? '✓' : '✗'} {result.feedback}</p>
                                      </div>
                                    ))}
                                  </div>
                                )}
                                {evalData.topics_to_review && evalData.topics_to_review.length > 0 && (
                                  <div className="topics-review-inline">
                                    <p><strong>Topics to Review:</strong> {evalData.topics_to_review.join(', ')}</p>
                                  </div>
                                )}
                                {evalData.feedback && (
                                  <div className="feedback-inline">
                                    <p><strong>Feedback:</strong> {evalData.feedback}</p>
                                  </div>
                                )}
                                </div>
                              )
                            })()}
                          </div>
                        </div>
                      ) : (
                        <div className="message-content">
                          {msg.content ? (
                            msg.content.split('\n').map((line, i) => (
                              <React.Fragment key={i}>
                                {line.startsWith('**') && line.endsWith('**') ? (
                                  <strong>{line.replace(/\*\*/g, '')}</strong>
                                ) : (
                                  line
                                )}
                                {i < msg.content.split('\n').length - 1 && <br />}
                              </React.Fragment>
                            ))
                          ) : (
                            <span className="typing-indicator">
                              <span className="typing-dots">
                                <span>.</span><span>.</span><span>.</span>
                              </span>
                            </span>
                          )}
                        </div>
                      )}
                      {msg.role === 'assistant' && isStreaming && idx === messages.length - 1 && !msg.quizData && (
                        <span className="streaming-indicator">▋</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Chat Input Area - Always visible */}
            <div className="chat-input-area">
              <form onSubmit={handleSendMessage} className="chat-input-form">
                <div className="input-wrapper">
                  <input
                    ref={chatInputRef}
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder={selectedTopic ? "Ask a question about this topic..." : "Select a topic to start chatting"}
                    className="chat-input"
                    disabled={loading || !selectedTopic}
                  />
                  <div className="input-actions">
                    <button
                      type="button"
                      onClick={handleGenerateSummary}
                      className="action-button-icon"
                      disabled={loading || !selectedTopic}
                      title="Generate Summary"
                    >
                      📄
                    </button>
                    <button
                      type="button"
                      onClick={handleGenerateQuiz}
                      className="action-button-icon"
                      disabled={loading || !selectedTopic}
                      title="Generate Quiz"
                    >
                      ✏️
                    </button>
                    <button 
                      type="submit" 
                      className="send-button-icon" 
                      disabled={loading || !inputMessage.trim() || !selectedTopic}
                      title="Send message"
                    >
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <line x1="22" y1="2" x2="11" y2="13"></line>
                        <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                      </svg>
                    </button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

export default App

