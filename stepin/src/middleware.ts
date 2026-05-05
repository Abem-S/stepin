import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  let supabaseResponse = NextResponse.next({ request })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll()
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value))
          supabaseResponse = NextResponse.next({ request })
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options)
          )
        },
      },
    }
  )

  const { data: { user } } = await supabase.auth.getUser()
  const userRole = user?.user_metadata?.role || 'student'

  // Protect professional routes
  if (request.nextUrl.pathname.startsWith('/professional')) {
    if (!user) {
      const url = request.nextUrl.clone()
      url.pathname = '/auth/login'
      url.searchParams.set('role', 'professional')
      url.searchParams.set('redirectTo', request.nextUrl.pathname)
      return NextResponse.redirect(url)
    }
    // Wrong role — redirect to their actual dashboard
    if (userRole !== 'professional') {
      const url = request.nextUrl.clone()
      url.pathname = '/student'
      url.search = ''
      return NextResponse.redirect(url)
    }
  }

  // Protect student dashboard routes
  if (request.nextUrl.pathname.startsWith('/student')) {
    if (!user) {
      const url = request.nextUrl.clone()
      url.pathname = '/auth/login'
      url.searchParams.set('role', 'student')
      url.searchParams.set('redirectTo', request.nextUrl.pathname)
      return NextResponse.redirect(url)
    }
    // Wrong role — redirect to their actual dashboard
    if (userRole !== 'student') {
      const url = request.nextUrl.clone()
      url.pathname = '/professional'
      url.search = ''
      return NextResponse.redirect(url)
    }
  }

  // Redirect logged-in users away from auth page
  if (request.nextUrl.pathname.startsWith('/auth/login')) {
    if (user) {
      const redirectTo = request.nextUrl.searchParams.get('redirectTo')
      const url = request.nextUrl.clone()
      url.pathname = redirectTo || (userRole === 'professional' ? '/professional' : '/student')
      url.search = ''
      return NextResponse.redirect(url)
    }
  }

  return supabaseResponse
}

export const config = {
  matcher: ['/professional/:path*', '/student/:path*', '/auth/:path*'],
}
