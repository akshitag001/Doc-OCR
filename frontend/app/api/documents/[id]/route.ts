import { NextRequest, NextResponse } from 'next/server';

export async function DELETE(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;

    // Forward the request to the FastAPI backend
    const response = await fetch(`http://localhost:8000/api/documents/${id}`, {
      method: 'DELETE',
    });

    // Check if response is ok (204 No Content is expected)
    if (response.status === 204) {
      return new NextResponse(null, { status: 204 });
    }

    // Handle other cases
    if (!response.ok) {
      if (response.status === 404) {
        return NextResponse.json(
          { error: 'Job not found' },
          { status: 404 }
        );
      }
      return NextResponse.json(
        { error: 'Backend error' },
        { status: response.status }
      );
    }

    return new NextResponse(null, { status: 204 });
  } catch (error) {
    console.error('API proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to delete document' },
      { status: 500 }
    );
  }
}
