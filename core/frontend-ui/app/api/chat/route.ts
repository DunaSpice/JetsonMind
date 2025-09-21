import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const { messages } = await request.json()
    const lastMessage = messages[messages.length - 1]
    
    // Call our Folder B agent server
    const response = await fetch('http://localhost:8001/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: lastMessage.content,
        conversation_id: null
      })
    })
    
    if (!response.ok) {
      throw new Error('Agent server error')
    }
    
    const result = await response.json()
    
    return NextResponse.json({
      id: Date.now().toString(),
      role: 'assistant',
      content: result.response,
      model: result.model_used
    })
    
  } catch (error) {
    console.error('Chat API error:', error)
    return NextResponse.json(
      { error: 'Failed to process message' },
      { status: 500 }
    )
  }
}
