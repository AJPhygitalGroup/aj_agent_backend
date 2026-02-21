'use client'

import { useState, useEffect, useRef } from 'react'
import { Upload, Trash2, Image, Type, FileImage, Palette, RefreshCw, Download } from 'lucide-react'

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

interface TemplateFile {
  name: string
  size: number
  type: string
  url?: string
  modified?: string
}

interface TemplatesData {
  templates: TemplateFile[]
  brand_assets: TemplateFile[]
  fonts: { name: string; size: number }[]
}

export default function BrandTemplatesPage() {
  const [data, setData] = useState<TemplatesData | null>(null)
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [uploadCategory, setUploadCategory] = useState<'template' | 'logo' | 'font'>('template')

  const fetchTemplates = async () => {
    try {
      const res = await fetch(`${BACKEND}/api/templates`)
      if (res.ok) {
        const json = await res.json()
        setData(json)
      }
    } catch (err) {
      console.error('Failed to fetch templates:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTemplates()
  }, [])

  const handleUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return

    setUploading(true)
    setUploadStatus(null)

    let successCount = 0
    let errorCount = 0

    for (let i = 0; i < files.length; i++) {
      const file = files[i]
      const formData = new FormData()
      formData.append('file', file)
      formData.append('category', uploadCategory)

      try {
        const res = await fetch(`${BACKEND}/api/templates/upload`, {
          method: 'POST',
          body: formData,
        })
        if (res.ok) {
          successCount++
        } else {
          const err = await res.json()
          console.error(`Upload failed for ${file.name}:`, err)
          errorCount++
        }
      } catch (err) {
        console.error(`Upload error for ${file.name}:`, err)
        errorCount++
      }
    }

    setUploading(false)
    if (errorCount === 0) {
      setUploadStatus(`${successCount} archivo(s) subido(s) correctamente`)
    } else {
      setUploadStatus(`${successCount} subidos, ${errorCount} con error`)
    }

    // Refresh list
    fetchTemplates()

    // Clear file input
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const handleDelete = async (filename: string, category: string) => {
    if (!confirm(`¿Eliminar ${filename}?`)) return

    try {
      const res = await fetch(`${BACKEND}/api/templates/${filename}?category=${category}`, {
        method: 'DELETE',
      })
      if (res.ok) {
        fetchTemplates()
      }
    } catch (err) {
      console.error('Delete error:', err)
    }
  }

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const acceptFormats: Record<string, string> = {
    template: '.png,.jpg,.jpeg,.svg,.psd',
    logo: '.png,.jpg,.jpeg,.svg',
    font: '.ttf,.otf,.woff,.woff2',
  }

  if (loading) {
    return (
      <div className="max-w-4xl">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Brand & Templates</h1>
        <div className="animate-pulse space-y-4">
          <div className="h-32 bg-gray-100 rounded-xl" />
          <div className="h-48 bg-gray-100 rounded-xl" />
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Brand & Templates</h1>
          <p className="text-sm text-gray-500 mt-1">
            Sube plantillas, logos y fuentes para mantener la identidad de marca en todo el contenido generado
          </p>
        </div>
        <button
          onClick={() => fetchTemplates()}
          className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Upload Section */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Upload className="w-5 h-5 text-brand-blue" />
          Subir Archivos
        </h2>

        {/* Category selector */}
        <div className="flex gap-2 mb-4">
          {[
            { key: 'template' as const, label: 'Plantilla', icon: FileImage, desc: 'Fondos para posts, carruseles' },
            { key: 'logo' as const, label: 'Logo', icon: Image, desc: 'Logos de marca' },
            { key: 'font' as const, label: 'Fuente', icon: Type, desc: 'Tipografías (.ttf, .otf)' },
          ].map(({ key, label, icon: Icon, desc }) => (
            <button
              key={key}
              onClick={() => setUploadCategory(key)}
              className={`flex-1 p-3 rounded-lg border-2 text-left transition-all ${
                uploadCategory === key
                  ? 'border-brand-blue bg-brand-blue/5'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <Icon className={`w-4 h-4 ${uploadCategory === key ? 'text-brand-blue' : 'text-gray-400'}`} />
                <span className={`text-sm font-medium ${uploadCategory === key ? 'text-brand-blue' : 'text-gray-700'}`}>
                  {label}
                </span>
              </div>
              <p className="text-xs text-gray-400">{desc}</p>
            </button>
          ))}
        </div>

        {/* File input */}
        <div className="flex items-center gap-4">
          <input
            ref={fileInputRef}
            type="file"
            accept={acceptFormats[uploadCategory]}
            multiple
            onChange={(e) => handleUpload(e.target.files)}
            className="hidden"
            id="file-upload"
          />
          <label
            htmlFor="file-upload"
            className={`flex-1 border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              uploading
                ? 'border-gray-300 bg-gray-50 cursor-wait'
                : 'border-gray-300 hover:border-brand-blue hover:bg-brand-blue/5'
            }`}
          >
            {uploading ? (
              <div className="flex items-center justify-center gap-2 text-gray-500">
                <RefreshCw className="w-5 h-5 animate-spin" />
                <span>Subiendo...</span>
              </div>
            ) : (
              <>
                <Upload className="w-8 h-8 mx-auto text-gray-400 mb-2" />
                <p className="text-sm text-gray-600 font-medium">
                  Click para seleccionar archivos
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  Formatos: {acceptFormats[uploadCategory]}
                </p>
              </>
            )}
          </label>
        </div>

        {uploadStatus && (
          <div className={`mt-3 text-sm px-4 py-2 rounded-lg ${
            uploadStatus.includes('error')
              ? 'bg-red-50 text-red-700'
              : 'bg-green-50 text-green-700'
          }`}>
            {uploadStatus}
          </div>
        )}
      </div>

      {/* Templates */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <FileImage className="w-5 h-5 text-purple-500" />
          Plantillas ({data?.templates?.length || 0})
        </h2>
        <p className="text-xs text-gray-400 mb-4">
          Los agentes Visual Designer y Carousel Creator usarán estas plantillas como fondo base para mantener tu identidad visual
        </p>

        {!data?.templates?.length ? (
          <div className="text-center py-8 text-gray-400">
            <FileImage className="w-10 h-10 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No hay plantillas subidas</p>
            <p className="text-xs mt-1">Sube imágenes de fondo que quieras usar como base para tu contenido</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {data.templates.map((t) => (
              <div key={t.name} className="group relative border border-gray-200 rounded-lg overflow-hidden">
                <img
                  src={`${BACKEND}${t.url}`}
                  alt={t.name}
                  className="w-full h-32 object-cover"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="%23f3f4f6" width="100" height="100"/><text x="50" y="55" text-anchor="middle" fill="%239ca3af" font-size="12">No preview</text></svg>'
                  }}
                />
                <div className="p-2">
                  <p className="text-xs font-medium text-gray-700 truncate">{t.name}</p>
                  <p className="text-xs text-gray-400">{formatSize(t.size)}</p>
                </div>
                <button
                  onClick={() => handleDelete(t.name, 'template')}
                  className="absolute top-2 right-2 p-1 bg-red-500/80 text-white rounded opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Brand Assets (Logos) */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Image className="w-5 h-5 text-blue-500" />
          Logos & Brand Assets ({data?.brand_assets?.length || 0})
        </h2>

        {!data?.brand_assets?.length ? (
          <div className="text-center py-6 text-gray-400">
            <Image className="w-10 h-10 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No hay logos subidos</p>
            <p className="text-xs mt-1">Sube tu logo para que aparezca en thumbnails y slides</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {data.brand_assets.map((a) => (
              <div key={a.name} className="group relative border border-gray-200 rounded-lg p-3 text-center">
                <img
                  src={`${BACKEND}${a.url}`}
                  alt={a.name}
                  className="h-16 mx-auto object-contain mb-2"
                  onError={(e) => {
                    (e.target as HTMLImageElement).style.display = 'none'
                  }}
                />
                <p className="text-xs font-medium text-gray-700 truncate">{a.name}</p>
                <p className="text-xs text-gray-400">{formatSize(a.size)}</p>
                <button
                  onClick={() => handleDelete(a.name, 'logo')}
                  className="absolute top-1 right-1 p-1 bg-red-500/80 text-white rounded opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Fonts */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Type className="w-5 h-5 text-green-500" />
          Fuentes ({data?.fonts?.length || 0})
        </h2>
        <p className="text-xs text-gray-400 mb-4">
          Las fuentes subidas se usan para el texto overlay en las imágenes generadas. Se recomienda subir Inter (Regular, Bold, Medium).
        </p>

        {!data?.fonts?.length ? (
          <div className="text-center py-6 text-gray-400">
            <Type className="w-10 h-10 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No hay fuentes subidas</p>
            <p className="text-xs mt-1">Se usará la fuente del sistema como fallback</p>
          </div>
        ) : (
          <div className="space-y-2">
            {data.fonts.map((f) => (
              <div key={f.name} className="flex items-center justify-between px-4 py-2 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Type className="w-4 h-4 text-gray-400" />
                  <span className="text-sm font-medium text-gray-700">{f.name}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-gray-400">{formatSize(f.size)}</span>
                  <button
                    onClick={() => handleDelete(f.name, 'font')}
                    className="p-1 text-red-400 hover:text-red-600 rounded"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Brand Colors Preview */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Palette className="w-5 h-5 text-pink-500" />
          Colores de Marca
        </h2>
        <div className="flex gap-4">
          {[
            { name: 'Primary Blue', color: '#667eea' },
            { name: 'Secondary Purple', color: '#764ba2' },
            { name: 'Accent Pink', color: '#f093fb' },
            { name: 'Dark BG', color: '#1a1a2e' },
            { name: 'Text', color: '#333333' },
          ].map(({ name, color }) => (
            <div key={color} className="text-center">
              <div
                className="w-14 h-14 rounded-lg border border-gray-200 shadow-sm mb-1"
                style={{ backgroundColor: color }}
              />
              <p className="text-xs font-medium text-gray-600">{name}</p>
              <p className="text-xs text-gray-400 font-mono">{color}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
